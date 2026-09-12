"""RADIO: a station list (dial up/down to change station, same MenuState
pattern as SPECIAL/INV/DATA) plus a live waveform of whatever's actually
playing -- see game.modules.radio.playback for the real audio engine and
game.modules.radio.directory for the online-station check.

Stays `background=True` (unchanged from the original proof-of-concept): once
tuned, playback keeps running on its own thread regardless of which tab is
on screen, matching a real radio you don't have to keep staring at."""
import queue
import random
import threading

import esper
import pygame as pg

from core.components import Active, Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data.store import theme
from game.modules import registry
from game.modules.radio import directory, playback
from game.ui import UI_MARGIN, FooterState, MenuState, menu_right_column_left, render_text
from utils.settings import config

NODE_KEY = "radio"
STATIONS_NODE_KEY = "radio.stations"

_WAVEFORM_LEFT = menu_right_column_left()
_WAVEFORM_RECT = pg.Rect(_WAVEFORM_LEFT, 92, config.WIDTH - UI_MARGIN - _WAVEFORM_LEFT, 220)
_WAVEFORM_REDRAW_INTERVAL = 0.1

_STATUS_LABELS = {
    playback.STATE_IDLE: "TUNING...",
    playback.STATE_DOWNLOADING: "DOWNLOADING...",
    playback.STATE_PLAYING: "PLAYING",
    playback.STATE_ERROR: "ERROR",
}

# "No clear signal" audio feedback, reusing sounds the project already had
# on disk but never wired up. Fallout-context choice: a plain static bed
# for "this station errored out / hasn't started yet" (dead air), and the
# tuning-specific static loops for the FM/AM stub specifically (searching
# across frequencies reads differently from a station that's simply down).
_STATIC_BACKGROUND_KEY = "radio_static_background"
_STATIC_TUNING_KEYS = ["radio_static_tuning_1", "radio_static_tuning_2", "radio_static_tuning_3"]

_menu_ent = None
_waveform_ent = None
_footer_ent = None
_discovery_queue: "queue.Queue[list]" = queue.Queue()

_static_channel = None
_static_kind = None  # None | "background" | "tuning" -- avoids restarting the same loop every tick


def register(pipboy):
    global _menu_ent, _waveform_ent, _footer_ent

    stations = playback.list_station_keys()
    registry.create_node(NODE_KEY, "RADIO", background=True)
    _menu_ent = registry.create_node(STATIONS_NODE_KEY, "", parent=NODE_KEY, background=True, components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1),
        MenuState(items=stations, max_items=9, on_change=_on_station_change),
    ])
    _waveform_ent = _register_waveform_panel()
    _footer_ent = _register_footer()

    if config.SOUND_ENABLED:
        ResourceLoader.add_sound("radio_on", "sounds/Radio/UI_Pipboy_Radio_On.mp3")
        ResourceLoader.add_sound("radio_off", "sounds/Radio/UI_Pipboy_Radio_Off.mp3")
        ResourceLoader.add_sound(_STATIC_BACKGROUND_KEY, "sounds/Radio/UI_Pipboy_Radio_StaticBackground_LP.wav")
        for i, key in enumerate(_STATIC_TUNING_KEYS, start=1):
            ResourceLoader.add_sound(key, f"sounds/Radio/StaticTuning/UI_Pipboy_Radio_StaticTuning_{i:02d}_LP.wav")

    esper.set_handler("node_resumed", _on_node_resumed)
    esper.set_handler("node_paused", _on_node_paused)
    esper.add_processor(_RadioTickProcessor(), priority=15)

    threading.Thread(target=_discover_online_stations, daemon=True).start()


def _register_waveform_panel():
    return esper.create_entity(
        Position(_WAVEFORM_RECT.left, _WAVEFORM_RECT.top), Renderable(image=_render_waveform(None)),
        Layer(5), Dirty(1), OwnedBy(STATIONS_NODE_KEY))


def _register_footer():
    footer_state = FooterState(sections=["NO STATION", "", ""])
    return esper.create_entity(
        Position(UI_MARGIN, config.HEIGHT - 45), Renderable(), Layer(5), Dirty(1),
        footer_state, OwnedBy(NODE_KEY))


def _render_waveform(samples) -> pg.Surface:
    image = pg.Surface(_WAVEFORM_RECT.size)
    image.fill(theme.bg_color)
    color = theme.draw_color
    dim = tuple(c * 0.4 for c in color)
    w, h = image.get_size()

    # Oscilloscope-style border + tick marks along the bottom/right edges,
    # matching the reference Pip-Boy RADIO screen's waveform panel.
    pg.draw.line(image, dim, (0, h - 1), (w - 1, h - 1))
    pg.draw.line(image, dim, (w - 1, 0), (w - 1, h - 1))
    for x in range(0, w, 12):
        pg.draw.line(image, dim, (x, h - 1), (x, h - 6))
    for y in range(0, h, 12):
        pg.draw.line(image, dim, (w - 1, y), (w - 6, y))

    if samples is not None and len(samples) > 1:
        normalized = samples.astype(float) / 32768.0
        mid_y = h / 2
        step = w / (len(samples) - 1)
        points = [(i * step, mid_y - s * mid_y * 0.9) for i, s in enumerate(normalized)]
        pg.draw.lines(image, color, False, points, 2)

    return image


def _refresh_footer(status: dict):
    footer_state = esper.component_for_entity(_footer_ent, FooterState)
    station_label = status["station"] or "NO STATION"
    state_label = _STATUS_LABELS.get(status["state"], status["state"].upper())
    if status["state"] == playback.STATE_ERROR and status["error"]:
        state_label = f"ERROR: {status['error']}".upper()

    changed_station = footer_state.update_section(0, station_label.upper())
    changed_state = footer_state.update_section(1, state_label)
    changed_profile = footer_state.update_section(2, status["profile"].upper())
    if changed_station or changed_state or changed_profile:
        esper.component_for_entity(_footer_ent, Dirty).state = 1


def _on_station_change(index: int):
    menu_state = esper.component_for_entity(_menu_ent, MenuState)
    if 0 <= index < len(menu_state.items):
        playback.tune(menu_state.items[index])
        _refresh_footer(playback.get_status())


def _on_node_resumed(key):
    if key == NODE_KEY:
        if config.SOUND_ENABLED:
            ResourceLoader.get_sound("radio_on").play()
        # Auto-tune whatever station is currently highlighted the first time
        # RADIO is ever opened -- like a real radio already tuned to
        # something when you switch it on, rather than silent until the
        # user manually turns the dial once.
        if playback.get_status()["station"] is None:
            menu_state = esper.component_for_entity(_menu_ent, MenuState)
            if menu_state.items:
                _on_station_change(menu_state.selected)


def _on_node_paused(key):
    if key == NODE_KEY and config.SOUND_ENABLED:
        ResourceLoader.get_sound("radio_off").play()


def _discover_online_stations():
    """Background thread: checks the free online radio directory (see
    directory.py) and merges any real, currently-verified-online stations
    into the tunable set -- never touches esper/pygame state directly (see
    _DiscoveryProcessor's queue drain), same convention as MAP's worker."""
    found = directory.get_online_stations(config.RADIO_ONLINE_STATION_COUNT)
    if not found:
        return

    existing = set(playback.list_station_keys())
    extra = {}
    for entry in found:
        key = _unique_key(entry["name"], existing)
        existing.add(key)
        extra[key] = {"source": "stream", "url": entry["url"], "profile": "clean"}

    playback.add_stations(extra)
    _discovery_queue.put(list(extra.keys()))


def _unique_key(name: str, existing: set) -> str:
    key = name.strip() or "Online Station"
    if key not in existing:
        return key
    i = 2
    while f"{key} ({i})" in existing:
        i += 1
    return f"{key} ({i})"


def _update_static(status: dict):
    """Plays "no clear signal" static in place of real audio while a
    station errored out or hasn't started producing sound yet, and a
    tuning-specific static loop for the FM/AM stub -- reusing sound assets
    the project already had on disk. Runs unconditionally (not gated on
    Active), matching how the real pyaudio playback also isn't gated on
    Active: RADIO's audio (real or, here, its stand-in) keeps going
    regardless of which tab is on screen."""
    global _static_channel, _static_kind
    if not config.SOUND_ENABLED:
        return

    if status["state"] == playback.STATE_PLAYING:
        desired_kind = None
    elif status["station"] is None:
        desired_kind = None
    elif status["source"] == "tuner":
        desired_kind = "tuning"
    else:
        desired_kind = "background"

    if desired_kind == _static_kind:
        return

    if _static_channel is not None:
        _static_channel.stop()
        _static_channel = None

    if desired_kind == "background":
        _static_channel = ResourceLoader.get_sound(_STATIC_BACKGROUND_KEY).play(loops=-1)
    elif desired_kind == "tuning":
        _static_channel = ResourceLoader.get_sound(random.choice(_STATIC_TUNING_KEYS)).play(loops=-1)

    _static_kind = desired_kind


class _RadioTickProcessor(esper.Processor):
    """Keeps the "no signal" static in sync every frame (audio feedback,
    same "runs regardless of Active" rule as real playback), and -- only
    while RADIO is actually on screen, throttled to a few times a second --
    redraws the waveform and refreshes the footer from playback.py's
    background thread."""

    def __init__(self):
        self._elapsed = 0.0

    def process(self, dt):
        status = playback.get_status()
        _update_static(status)

        while True:
            try:
                new_keys = _discovery_queue.get_nowait()
            except queue.Empty:
                break
            menu_state = esper.component_for_entity(_menu_ent, MenuState)
            menu_state.items.extend(new_keys)
            esper.component_for_entity(_menu_ent, Dirty).state = 1

        if not esper.has_component(_waveform_ent, Active):
            return
        self._elapsed += dt
        if self._elapsed < _WAVEFORM_REDRAW_INTERVAL:
            return
        self._elapsed = 0.0

        _refresh_footer(status)

        show_waveform = status["state"] == playback.STATE_PLAYING and status["waveform_enabled"]
        samples = playback.get_waveform() if show_waveform else None
        esper.component_for_entity(_waveform_ent, Renderable).image = _render_waveform(samples)
        esper.component_for_entity(_waveform_ent, Dirty).state = 1
