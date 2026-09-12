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

Stations themselves come from two places, merged: assets/data/radio_stations.json
(shipped defaults, via game.data.catalog) and SaveData.custom_radios
(save/state.json, user-added -- same RadioStation shape, wins on a matching
`title`) -- same "catalog vs. save data" split already used for
items/quests/perks elsewhere in this app, rather than a hardcoded config
default. Both validate against game.data.radio_models.RadioStation.

Each station picks a distortion profile (assets/data/radio_profiles.json,
via `profile` -- "clean"/no distortion when omitted) -- an ffmpeg audio
filter chain applied to the same decode pipeline, so the waveform
naturally reflects whatever distortion is actually audible rather than a
separate pre-filter signal. A profile can also turn the waveform off
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
from game.data.radio_models import RadioProfile, RadioStation
from game.data.store import save_data
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
_DEFAULT_PROFILE = RadioProfile(label="Clean", filters=[], waveform_enabled=True)


def _stations_by_title(stations) -> dict:
    return {station.title: station for station in stations}


# Seeded from the shipped catalog + the user's own save-data additions
# (custom_radios wins on a matching title); game/modules/radio/__init__.py
# also merges in stations found via the online directory check
# (directory.py) at runtime through add_stations() -- kept here (not read
# from their sources directly at the call site) so every station, whatever
# it came from, resolves through the exact same tune()/_run() path.
_stations: dict[str, RadioStation] = {
    **_stations_by_title(catalog.radio_stations), **_stations_by_title(save_data.custom_radios),
}

_lock = threading.Lock()
_current_key: Optional[str] = None
_current_source = "local"
_state = STATE_IDLE
_error_message = ""
_profile_label = _DEFAULT_PROFILE.label
_current_profile_key = _DEFAULT_PROFILE_KEY
_waveform_enabled = _DEFAULT_PROFILE.waveform_enabled
# A runtime-only (never persisted) override that wins over the current
# station's own configured `profile`, set by cycle_profile() -- Left/Right
# on the keyboard. Cleared on every fresh tune() so a new station always
# starts at its own intended default rather than inheriting whatever was
# last dialed in.
_profile_override: Optional[str] = None
_waveform = np.zeros(CHUNK, dtype=np.int16)
# True while the radio has been explicitly turned off (space bar) --
# distinct from STATE_ERROR/STATE_DOWNLOADING, which mean "on, but not
# producing sound yet/right now". _current_key is deliberately NOT cleared
# on pause, so resume() knows what to restart.
_paused = False
_generation = 0  # bumped by every tune()/stop() so a stale worker retires itself
_current_process = None  # the live ffmpeg subprocess (if any) -- killed directly by tune()/stop()

_pyaudio_instance: Optional[pyaudio.PyAudio] = None

# station_key -> fraction downloaded so far (0..1), only present while a
# boot-time preload (make_preload_task) or a lazy tune()-triggered download
# is actually in flight -- read by the loading screen for a real progress
# bar instead of a simulated fill.
_download_progress: dict = {}


def add_stations(extra: dict):
    """Merges additional {title: RadioStation} entries (e.g. from the
    online directory check) into the tunable station set, alongside the
    catalog + custom_radios defaults."""
    _stations.update(extra)


def list_station_keys() -> list:
    return list(_stations.keys())


def get_station_source(station_key: str) -> str:
    """The station's own `source` field ("local"/"youtube"/"stream"/
    "tuner"), without tuning it -- used to sort stations into RADIO's
    STATIONS/TUNER/SIGNAL submodules (game/modules/radio/__init__.py)."""
    station = _stations.get(station_key)
    return station.source if station else "local"


def get_station_description(station_key: str) -> Optional[str]:
    """The station's own `description`, if any -- shown below the waveform
    panel while it's playing (game/modules/radio/__init__.py)."""
    station = _stations.get(station_key)
    return station.description if station else None


def youtube_station_keys() -> list:
    """Every configured station (catalog + custom_radios -- not the online
    directory, which is always `source: "stream"`, never a download) that
    needs a YouTube download. Used to build one boot-loading task per
    station -- see make_preload_task()."""
    return [key for key, station in _stations.items() if station.source == "youtube"]


def is_downloaded(station_key: str) -> bool:
    """True if `station_key` needs no (further) download -- not a YouTube
    station at all, or already cached from a previous run."""
    station = _stations.get(station_key)
    if not station or station.source != "youtube":
        return True
    return os.path.exists(_youtube_cache_path(station_key))


def _youtube_cache_path(station_key: str) -> str:
    return os.path.join(config.RADIO_CACHE_DIR, f"{station_key}.mp3")


def make_preload_task(station_key: str):
    """Returns a callable for boot/loading.py's task list that downloads
    `station_key` ahead of time if it isn't already cached, so opening
    RADIO doesn't hit a fresh multi-second download on top of everything
    else. Follows the loading task-list convention: returns a float in
    [0, 1) while a download is genuinely in progress (real byte progress
    from yt-dlp's own hook, not simulated -- see _download_youtube()), and
    True once the file actually exists on disk (not just "yt-dlp says
    finished", since the ffmpeg postprocessing step still has to run after
    that). True immediately if there's nothing to download at all, and also
    True once the worker thread finishes even on failure -- a bad/dead URL
    must give up, not hang the entire boot sequence waiting for a file that
    will never appear (get_status() will show the real error once the
    station is actually tuned)."""
    state = {"started": False, "done": False}

    def step():
        if is_downloaded(station_key):
            return True
        if not state["started"]:
            state["started"] = True
            threading.Thread(target=_preload_worker, args=(station_key, state), daemon=True).start()
        if state["done"]:
            return True
        return _download_progress.get(station_key, 0.0)

    return step


def _preload_worker(station_key: str, state: dict):
    try:
        station = _stations.get(station_key)
        if not station or not station.url:
            return
        cache_path = _youtube_cache_path(station_key)
        os.makedirs(config.RADIO_CACHE_DIR, exist_ok=True)
        try:
            _download_youtube(station.url, cache_path, progress_key=station_key)
        except Exception as exc:
            logger.debug(f"Radio preload failed for {station_key!r}: {exc}")
    finally:
        _download_progress.pop(station_key, None)
        state["done"] = True


def get_status() -> dict:
    with _lock:
        return {
            "station": _current_key, "source": _current_source,
            "state": _state, "error": _error_message,
            "profile": _profile_label, "waveform_enabled": _waveform_enabled,
            "paused": _paused,
        }


def is_paused() -> bool:
    with _lock:
        return _paused


def get_waveform() -> np.ndarray:
    with _lock:
        return _waveform.copy()


def tune(station_key: str):
    """Switches playback to `station_key` (a key from the catalog, save
    data, or online directory -- see list_station_keys()). Stops
    whatever was playing and starts resolving/playing the new one in the
    background; returns immediately either way. Always resets any
    profile override from cycle_profile() -- a freshly tuned station
    starts at its own configured default, not whatever was last dialed in
    on a different station."""
    global _profile_override
    _profile_override = None
    _restart(station_key)


def pause():
    """Turns the radio off (space bar): stops audio but remembers the
    current station so resume() can pick it back up. No-op if nothing is
    tuned or it's already paused."""
    global _paused, _generation
    if _current_key is None or _paused:
        return
    _kill_current_process()
    with _lock:
        _generation += 1  # retire whatever thread was running, same as stop()
        _paused = True
    _set_state(STATE_IDLE)


def resume():
    """Turns the radio back on (space bar) at whatever was last tuned.
    No-op if nothing was ever tuned or it isn't currently paused."""
    if _current_key is None or not _paused:
        return
    _restart(_current_key)


def toggle():
    if is_paused():
        resume()
    else:
        pause()


def list_profile_keys() -> list:
    return list(catalog.radio_profiles.keys())


def cycle_profile(direction: int):
    """Switches the currently-playing station to the next/previous
    distortion profile (direction=+1/-1) and restarts it from the
    beginning -- a runtime-only override for this session (see
    _profile_override), never written back to the station's own config.
    No-op if nothing is tuned or no profiles are defined."""
    global _profile_override
    if _current_key is None:
        return
    keys = list_profile_keys()
    if not keys:
        return
    with _lock:
        current = _current_profile_key
    try:
        index = keys.index(current)
    except ValueError:
        index = 0
    _profile_override = keys[(index + direction) % len(keys)]
    _restart(_current_key)


def _restart(station_key: str):
    # Any real restart means "actively playing something now" by
    # construction -- centralized here so tune()/resume()/cycle_profile()
    # (every caller) don't each have to remember to clear it themselves.
    global _current_key, _state, _error_message, _generation, _paused
    _kill_current_process()
    with _lock:
        _generation += 1
        my_generation = _generation
        _current_key = station_key
        _state = STATE_IDLE
        _error_message = ""
        _paused = False
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


def _set_profile_info(profile: RadioProfile, profile_key: str, source: str):
    global _profile_label, _current_profile_key, _waveform_enabled, _current_source
    with _lock:
        _profile_label = profile.label
        _current_profile_key = profile_key
        _waveform_enabled = profile.waveform_enabled
        _current_source = source


def _get_profile(name: Optional[str]) -> RadioProfile:
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
    # reflect the right profile immediately, even while still downloading.
    # A runtime cycle_profile() override wins over the station's own
    # configured `profile`; "clean" (no distortion) is the fallback when
    # neither is set.
    profile_key = _profile_override or station.profile or _DEFAULT_PROFILE_KEY
    profile = _get_profile(profile_key)
    _set_profile_info(profile, profile_key, station.source)

    path = _resolve_path(station, station_key, generation)
    if path is None or not _is_current(generation):
        return

    _play_loop(path, generation, profile)


def _resolve_path(station: RadioStation, station_key: str, generation) -> Optional[str]:
    source = station.source

    if source == "local":
        full_path = os.path.join(config.ASSETS_FOLDER, "sounds", "radio", station.path or "")
        if not os.path.exists(full_path):
            _set_state(STATE_ERROR, f"file not found: {station.path}")
            return None
        return full_path

    if source == "youtube":
        cache_path = _youtube_cache_path(station_key)
        if os.path.exists(cache_path):
            return cache_path
        if not station.url:
            _set_state(STATE_ERROR, "missing youtube url")
            return None
        _set_state(STATE_DOWNLOADING)
        os.makedirs(config.RADIO_CACHE_DIR, exist_ok=True)
        try:
            _download_youtube(station.url, cache_path, progress_key=station_key)
        except Exception as exc:
            logger.debug(f"Radio YouTube download failed: {exc}")
            _set_state(STATE_ERROR, "download failed")
            return None
        finally:
            _download_progress.pop(station_key, None)
        if not _is_current(generation):
            return None
        return cache_path

    if source == "stream":
        # A real, currently-broadcasting internet radio stream -- played
        # live via ffmpeg (which accepts a URL as input transparently, same
        # as a local file), never downloaded/cached, unlike "youtube".
        if not station.url:
            _set_state(STATE_ERROR, "missing stream url")
            return None
        return station.url

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


def _download_youtube(url: str, out_path: str, progress_key: Optional[str] = None):
    import yt_dlp  # heavy import -- only needed on an actual download

    def on_progress(info):
        if progress_key is None:
            return
        if info.get("status") == "downloading":
            total = info.get("total_bytes") or info.get("total_bytes_estimate")
            downloaded = info.get("downloaded_bytes")
            if total:
                # Capped below 1.0 -- yt-dlp's own "finished" still leaves
                # the FFmpegExtractAudio postprocessing step to run, so the
                # real completion signal is the output file actually
                # existing (see is_downloaded()), not this hook.
                _download_progress[progress_key] = min(0.95, downloaded / total)

    out_template = out_path[:-len(".mp3")] + ".%(ext)s"
    options = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
        "progress_hooks": [on_progress] if progress_key else [],
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])


def _play_loop(path: str, generation, profile: RadioProfile):
    global _pyaudio_instance, _current_process
    if _pyaudio_instance is None:
        _pyaudio_instance = pyaudio.PyAudio()
    stream = _pyaudio_instance.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, output=True)

    filters = profile.filters
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
