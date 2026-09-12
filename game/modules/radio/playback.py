"""Real RADIO audio: a local file plays directly and loops forever; a
YouTube-sourced station is downloaded once (via yt-dlp, needs network) into
a local cache and played from that copy from then on; a "stream" station is
a real internet radio stream (see game.modules.radio.directory), played
live and never cached, same as tuning an actual station. Only "youtube"
needs the download-once-then-cache treatment -- mirrors the philosophy
already used for MAP's OSM data.

Decoding + playback uses ffmpeg (already a project dependency, and the
system `ffmpeg` binary it shells out to) piped into PyAudio as raw PCM --
this also hands us the raw samples needed for a real (not simulated)
waveform, at the cost of a second, independent audio backend alongside
pygame's own mixer (used for UI clicks/hum/chimes elsewhere in the app).

Each station picks a distortion profile (assets/data/radio_profiles.json,
via `profile` in config.RADIOS -- "clean"/no distortion when omitted) --
an ffmpeg audio filter chain applied to the same decode pipeline, so the
waveform naturally reflects whatever distortion is actually audible rather
than a separate pre-filter signal. A profile can also turn the waveform off
entirely (some distortion makes it unreadable noise anyway).

Runs entirely off the main thread. `tune()`/`stop()` return immediately, but
still directly kill whatever ffmpeg subprocess is currently live before
returning -- important because the playback thread spends most of its time
blocked inside a synchronous `process.stdout.read()` call, so a purely
cooperative "notice a generation counter changed" scheme wouldn't unblock it
promptly (or at all, if ffmpeg itself ever wedges). Killing the process
directly forces that read to return immediately, so the old thread wakes up,
sees its generation is stale, and closes its own PyAudio stream right after.
"""
import os
import subprocess
import threading
from typing import Optional

import ffmpeg
import numpy as np
import pyaudio

from game.data import catalog
from utils.logger import logger
from utils.settings import config

CHUNK = 1024
RATE = 44100
CHANNELS = 1

STATE_IDLE = "idle"
STATE_DOWNLOADING = "downloading"
STATE_PLAYING = "playing"
STATE_ERROR = "error"

_DEFAULT_PROFILE_KEY = "clean"
_DEFAULT_PROFILE = {"label": "Clean", "filters": [], "waveform_enabled": True}

# Seeded from config.RADIOS; game/modules/radio/__init__.py merges in
# stations found via the online directory check (directory.py) at runtime
# through add_stations() -- kept here (not read from config.RADIOS
# directly) so both sources resolve through the exact same tune()/_run()
# path instead of duplicating lookup logic at the call site.
_stations: dict = dict(config.RADIOS)

_lock = threading.Lock()
_current_key: Optional[str] = None
_current_source = "local"
_state = STATE_IDLE
_error_message = ""
_profile_label = _DEFAULT_PROFILE["label"]
_waveform_enabled = _DEFAULT_PROFILE["waveform_enabled"]
_waveform = np.zeros(CHUNK, dtype=np.int16)
_generation = 0  # bumped by every tune()/stop() so a stale worker retires itself
_current_process = None  # the live ffmpeg subprocess (if any) -- killed directly by tune()/stop()

_pyaudio_instance: Optional[pyaudio.PyAudio] = None


def add_stations(extra: dict):
    """Merges additional {key: station_dict} entries (e.g. from the online
    directory check) into the tunable station set, alongside config.RADIOS."""
    _stations.update(extra)


def list_station_keys() -> list:
    return list(_stations.keys())


def get_status() -> dict:
    with _lock:
        return {
            "station": _current_key, "source": _current_source,
            "state": _state, "error": _error_message,
            "profile": _profile_label, "waveform_enabled": _waveform_enabled,
        }


def get_waveform() -> np.ndarray:
    with _lock:
        return _waveform.copy()


def tune(station_key: str):
    """Switches playback to `station_key` (a key in config.RADIOS). Stops
    whatever was playing and starts resolving/playing the new one in the
    background; returns immediately either way."""
    global _current_key, _state, _error_message, _generation
    _kill_current_process()
    with _lock:
        _generation += 1
        my_generation = _generation
        _current_key = station_key
        _state = STATE_IDLE
        _error_message = ""
    threading.Thread(target=_run, args=(station_key, my_generation), daemon=True).start()


def stop():
    """Stops playback entirely -- e.g. app shutdown, so a real ffmpeg
    subprocess doesn't get left running (orphaned) after the interpreter
    exits. Kills the live subprocess directly rather than just asking the
    background thread to stop, since it's usually blocked in a synchronous
    read and wouldn't notice in time otherwise."""
    global _current_key, _generation
    _kill_current_process()
    with _lock:
        _generation += 1
        _current_key = None


def _kill_current_process():
    global _current_process
    with _lock:
        process, _current_process = _current_process, None
    if process is not None:
        try:
            process.kill()
        except Exception:
            pass


def _set_state(state, error=""):
    global _state, _error_message
    with _lock:
        _state = state
        _error_message = error


def _set_profile_info(profile: dict, source: str):
    global _profile_label, _waveform_enabled, _current_source
    with _lock:
        _profile_label = profile.get("label", _DEFAULT_PROFILE["label"])
        _waveform_enabled = bool(profile.get("waveform_enabled", True))
        _current_source = source


def _get_profile(name: Optional[str]) -> dict:
    profiles = catalog.radio_profiles
    return profiles.get(name or _DEFAULT_PROFILE_KEY) or profiles.get(_DEFAULT_PROFILE_KEY) or _DEFAULT_PROFILE


def _is_current(generation) -> bool:
    with _lock:
        return generation == _generation


def _run(station_key, generation):
    station = _stations.get(station_key)
    if not station:
        _set_state(STATE_ERROR, "unknown station")
        return

    # Resolved once up front (not per-loop-iteration) so the footer/waveform
    # reflect the station's own configured profile immediately, even while
    # still downloading -- "clean" (no distortion) whenever a station
    # doesn't specify one.
    profile = _get_profile(station.get("profile"))
    _set_profile_info(profile, station.get("source", "local"))

    path = _resolve_path(station, station_key, generation)
    if path is None or not _is_current(generation):
        return

    _play_loop(path, generation, profile)


def _resolve_path(station: dict, station_key: str, generation) -> Optional[str]:
    source = station.get("source", "local")

    if source == "local":
        full_path = os.path.join(config.ASSETS_FOLDER, "sounds", "radio", station.get("path", ""))
        if not os.path.exists(full_path):
            _set_state(STATE_ERROR, f"file not found: {station.get('path', '')}")
            return None
        return full_path

    if source == "youtube":
        cache_path = os.path.join(config.RADIO_CACHE_DIR, f"{station_key}.mp3")
        if os.path.exists(cache_path):
            return cache_path
        _set_state(STATE_DOWNLOADING)
        os.makedirs(config.RADIO_CACHE_DIR, exist_ok=True)
        try:
            _download_youtube(station["url"], cache_path)
        except Exception as exc:
            logger.debug(f"Radio YouTube download failed: {exc}")
            _set_state(STATE_ERROR, "download failed")
            return None
        if not _is_current(generation):
            return None
        return cache_path

    if source == "stream":
        # A real, currently-broadcasting internet radio stream -- played
        # live via ffmpeg (which accepts a URL as input transparently, same
        # as a local file), never downloaded/cached, unlike "youtube".
        url = station.get("url")
        if not url:
            _set_state(STATE_ERROR, "missing stream url")
            return None
        return url

    if source == "tuner":
        if not config.LOCAL_RADIO_AVAILABLE:
            _set_state(STATE_ERROR, "FM/AM tuner not enabled")
        else:
            # Real hardware bring-up is out of scope here -- this project
            # doesn't have a specific FM/AM receiver's driver/API to target
            # yet. Flagged clearly rather than faking support.
            _set_state(STATE_ERROR, "FM/AM tuner hardware not wired up yet")
        return None

    _set_state(STATE_ERROR, f"unknown source: {source!r}")
    return None


def _download_youtube(url: str, out_path: str):
    import yt_dlp  # heavy import -- only needed on an actual download

    out_template = out_path[:-len(".mp3")] + ".%(ext)s"
    options = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])


def _play_loop(path: str, generation, profile: dict):
    global _pyaudio_instance, _current_process
    if _pyaudio_instance is None:
        _pyaudio_instance = pyaudio.PyAudio()
    stream = _pyaudio_instance.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, output=True)

    filters = profile.get("filters") or []
    output_kwargs = {"format": "s16le", "acodec": "pcm_s16le", "ac": CHANNELS, "ar": RATE}
    if filters:
        output_kwargs["af"] = ",".join(filters)

    try:
        while _is_current(generation):
            process = (
                ffmpeg.input(path)
                .output("pipe:", **output_kwargs)
                .run_async(pipe_stdout=True, pipe_stderr=subprocess.DEVNULL)
            )
            with _lock:
                _current_process = process
            _set_state(STATE_PLAYING)
            try:
                while _is_current(generation):
                    raw = process.stdout.read(CHUNK * 2)
                    if not raw:
                        break  # end of file -- loop back and restart it
                    stream.write(raw)
                    _set_waveform(raw)
            finally:
                process.kill()
                with _lock:
                    if _current_process is process:
                        _current_process = None
    except Exception as exc:
        logger.debug(f"Radio playback failed: {exc}")
        _set_state(STATE_ERROR, "playback failed")
    finally:
        stream.stop_stream()
        stream.close()


def _set_waveform(raw: bytes):
    global _waveform
    with _lock:
        _waveform = np.frombuffer(raw, dtype=np.int16).copy()
