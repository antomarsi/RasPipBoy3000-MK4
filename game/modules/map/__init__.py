import queue
import threading
import time
from datetime import datetime

import esper
import pygame as pg

from core.components import Active, Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game import location
from game.data.store import theme
from game import geo
from game.geo import project
from game.modules import registry
from game.modules.map import geocode, osm
from game.ui import UI_MARGIN, FooterState, fit_icon, render_text
from utils.settings import config

LOCAL_NODE_KEY = "map.local"
WORLD_NODE_KEY = "map.world"

# Same content area every other tab uses (below the header, above a footer).
_VIEWPORT = pg.Rect(UI_MARGIN, 92, config.WIDTH - UI_MARGIN * 2, config.HEIGHT - 92 - 55)

# The map is actually rendered into a buffer bigger than the viewport, and
# the viewport just crops a moving window out of it -- panning is then a
# cheap subsurface, not a re-render of (potentially tens of thousands of)
# road/building primitives. Once panning (LOCAL only) reaches the buffer's
# own edge, _recenter_local_if_needed() re-renders around a shifted center
# from the same already-cached geometry -- so continuing to push WASD keeps
# revealing more of the city instead of hard-stopping at a small fixed
# patch. A single buffer big enough to hold an entire city at street-level
# zoom without ever recentering would be gigabytes in size, so recentering
# (not one unbounded buffer) is what actually makes "pan across the whole
# city" feasible.
_BUFFER_SCALE = 2.5
_BUFFER_SIZE = (round(_VIEWPORT.width * _BUFFER_SCALE), round(_VIEWPORT.height * _BUFFER_SCALE))
_MAX_PAN = ((_BUFFER_SIZE[0] - _VIEWPORT.width) / 2.0, (_BUFFER_SIZE[1] - _VIEWPORT.height) / 2.0)
_RECENTER_THRESHOLD = 0.95  # fraction of _MAX_PAN that triggers a recenter

# Dead zone (game-design sense): the cursor moves freely inside this
# viewport-centered rect; only once it would cross the rect's edge does the
# camera start panning to compensate, so the cursor visually "pins" at the
# edge while the world scrolls under it -- standard 2D-camera-follow
# behavior. The cursor only continues past this rect toward the true
# viewport edge once panning has hit _MAX_PAN (nothing left to scroll to).
_DEADZONE_FRACTION = 0.5
_DEADZONE = pg.Rect(0, 0, _VIEWPORT.width * _DEADZONE_FRACTION, _VIEWPORT.height * _DEADZONE_FRACTION)
_DEADZONE.center = (_VIEWPORT.width / 2, _VIEWPORT.height / 2)

_POI_ICON_BOX = (20, 20)
_PLAYER_ICON_BOX = (24, 24)
# How often the worker rechecks location.get_location() while it's still
# None. This is a plain in-memory read (no network, no cost to poll often),
# so it stays short -- found by testing that a coarser value (previously
# 5.0) made the boot loading bar visibly freeze for several seconds
# whenever the very first location fix hadn't landed yet by the time this
# loop's first check ran, instead of picking it up within a fraction of a
# second of it actually becoming available.
_NO_FIX_POLL_S = 0.25
_MIN_RADIUS_M = 50.0
_ZOOM_FACTOR = 1.25
_CURSOR_SPEED_PX_S = 260.0
_HOVER_RADIUS_PX = _POI_ICON_BOX[0]
# Buildings fade out (both fill and border) as LOCAL zooms out -- fully
# opaque at street level, faint by the time you're zoomed out toward the
# whole city, so a wide view doesn't turn into a solid smear of outlines.
_BUILDING_FILL_OPACITY_NEAR = 0.15
_BUILDING_FILL_OPACITY_FAR = 0.03
_BUILDING_BORDER_OPACITY_NEAR = 1.0
_BUILDING_BORDER_OPACITY_FAR = 0.25
_GEOCODE_CELL_DEG = 0.01  # ~1km -- coarser than the OSM fetch's own cache
                          # granularity, so a stationary/jittering fix doesn't
                          # re-hit Nominatim on every worker tick.

# The real Pip-Boy's world map is a small handful of named locations, not
# every shop and doctor's office in the query radius -- only these marker
# categories show up when WORLD is the active tab. LOCAL is unfiltered.
_WORLD_IMPORTANT_ICONS = {
    "vault", "military", "settlement", "monument", "metro",
    "encampment", "cave", "ruins_town", "ruins_urban", "ruins_sewer",
}
# Same idea for roads/buildings on WORLD -- a whole city's worth of every
# residential street and building outline at once is illegible noise, not a
# map. Only major roads draw, and buildings don't draw at all (they're
# inherently street-level detail). LOCAL stays fully detailed.
_MAJOR_HIGHWAYS = {"motorway", "trunk", "primary", "secondary", "motorway_link", "trunk_link", "primary_link"}

_result_queue = queue.Queue()
_worker_thread = None
_local_entity = None
_world_entity = None
_local_overlay_entity = None
_world_overlay_entity = None
_icon_cache = {}
_player_icon_cache = {}

# The last real fetch (raw geometry + its center), kept on the main thread so
# zoom/pan/filter can re-render on demand without waiting on a new Overpass
# round-trip. Written by the worker thread, read from the main thread -- a
# plain reference swap, same convention as game.location.
_last_area = None
_last_center = None  # (lat, lon) the current buffers were actually rendered around
_fetched_radius_m = config.MAP_WORLD_RADIUS_M  # zoom-out ceiling: can't show
                                                # geometry that was never fetched

# LOCAL renders at a fixed street-level radius (like any normal map app
# zoomed in) regardless of the city's own size -- what scales with the city
# is how much gets *fetched* (city_radius, from reverse geocoding) so LOCAL
# can pan/recenter across the whole thing, and how far out the user can zoom
# (_fetched_radius_m, the ceiling _clamp_radius enforces).
_city_key = None
_local_radius = config.MAP_LOCAL_RADIUS_M
# WORLD renders at (approximately) the whole resolved city in one view --
# see _worker_loop.
_world_radius = config.MAP_WORLD_RADIUS_M
_local_buffer = None
_world_buffer = None
_local_pan = [0.0, 0.0]
_world_pan = [0.0, 0.0]
# LOCAL's own current view center -- starts equal to _last_center (the fetch
# center) but can drift via _recenter_local_if_needed() as the user pans
# across the city, independently of WORLD (which always shows the fetch
# center, since it's meant to show the whole city at a glance).
_local_center = None

_cursor = [_VIEWPORT.width / 2, _VIEWPORT.height / 2]
_hovered_poi = None
_filter_mode = False
_filter_text = ""

# The device's own live position/heading (independent of the map buffers,
# which only refresh occasionally) -- polled every frame so the "you are
# here" arrow moves smoothly between buffer refreshes, not just when a new
# Overpass fetch lands.
_live_lat = None
_live_lon = None
_live_heading = None


def register(pipboy):
    global _local_entity, _world_entity, _local_overlay_entity, _world_overlay_entity
    global _local_buffer, _world_buffer

    registry.create_node("map", "MAP")
    registry.create_node(LOCAL_NODE_KEY, "LOCAL", parent="map")
    registry.create_node(WORLD_NODE_KEY, "WORLD", parent="map")

    _local_buffer = _render_no_signal_buffer()
    _world_buffer = _render_no_signal_buffer()
    _local_entity = _register_map_surface(LOCAL_NODE_KEY, _local_buffer, _local_pan)
    _world_entity = _register_map_surface(WORLD_NODE_KEY, _world_buffer, _world_pan)
    _local_overlay_entity = _register_overlay(LOCAL_NODE_KEY)
    _world_overlay_entity = _register_overlay(WORLD_NODE_KEY)
    _register_local_footer()

    location.init()
    _start_worker()
    # Module-level functions, not closures -- esper.set_handler keeps only a
    # weak reference, same reasoning as registry.handle_action/audio._on_action.
    esper.set_handler("action", _on_map_action)
    esper.set_handler("key_text", _on_key_text)
    esper.set_handler("node_resumed", _on_node_resumed)
    esper.add_processor(_MapResultProcessor(), priority=20)
    esper.add_processor(_CursorMoveProcessor(), priority=25)


def make_warm_cache_task(timeout_s: float = 12.0):
    """Returns a callable for boot/loading.py's task list that waits for the
    worker thread (already started by register()) to resolve the current
    city and fetch or load its cached OSM data -- so LOCAL has real data the
    moment the user first opens MAP, instead of a "NO SIGNAL" placeholder
    that only fills in later in the background.

    Follows the loading task-list convention: the returned callable is
    invoked once per boot-loading frame and returns False to mean "still
    waiting, call me again next frame" -- unlike a single blocking sleep,
    this lets the loading screen actually render its label while it waits,
    instead of freezing on the previous task's label until this one
    finishes. Best-effort: with no fix or no Overpass connectivity within
    the timeout, it gives up and lets boot continue anyway with whatever
    ended up ready."""
    state: dict = {"deadline": None}

    def step():
        if state["deadline"] is None:
            state["deadline"] = time.monotonic() + timeout_s
        return _last_area is not None or time.monotonic() >= state["deadline"]

    return step


def _register_map_surface(node_key, buffer, pan):
    return esper.create_entity(
        Position(_VIEWPORT.left, _VIEWPORT.top), Renderable(image=_current_view(buffer, pan)),
        Layer(5), Dirty(1), OwnedBy(node_key))


def _register_overlay(node_key):
    # A separate, cheap-to-rebuild layer above the map surface -- the cursor
    # reticle, "you are here" arrow, hover tooltip and filter input box all
    # redraw on every keypress/GPS tick, and must never require re-drawing
    # the (potentially tens of thousands of primitives) map geometry
    # underneath just to move a cursor or nudge the arrow.
    return esper.create_entity(
        Position(_VIEWPORT.left, _VIEWPORT.top), Renderable(image=_render_overlay()),
        Layer(6), Dirty(1), OwnedBy(node_key))


def _register_local_footer():
    footer_state = FooterState(sections=["", "", ("LOCAL MAP", 2)])
    footer_ent = esper.create_entity(
        Position(UI_MARGIN, config.HEIGHT - 45), Renderable(), Layer(5), Dirty(1),
        footer_state, OwnedBy(LOCAL_NODE_KEY))
    esper.add_processor(_ClockFooterProcessor(footer_ent), priority=32)


def _start_worker():
    # Overpass/GPS/geocoding calls are seconds-slow -- this thread only ever
    # reads game.location and posts results to a queue.Queue; esper/pygame
    # state is touched only from _MapResultProcessor, on the main thread.
    global _worker_thread
    if _worker_thread is not None:
        return
    _worker_thread = threading.Thread(target=_worker_loop, daemon=True)
    _worker_thread.start()


def _worker_loop():
    global _last_area, _last_center, _fetched_radius_m
    global _city_key, _world_radius

    last_geo_key = None
    last_fetched_city = None
    while True:
        fix = location.get_location()
        if fix is None:
            time.sleep(_NO_FIX_POLL_S)
            continue

        lat, lon, _source, _heading = fix
        geo_key = (round(lat / _GEOCODE_CELL_DEG), round(lon / _GEOCODE_CELL_DEG))
        if geo_key != last_geo_key:
            result = geocode.reverse_geocode(lat, lon)
            if result is not None:
                _city_key, city_radius = result
                # WORLD shows (approximately) the whole city in one view --
                # LOCAL stays at its own fixed street-level zoom regardless
                # of city size (see _local_radius's own comment); city_radius
                # only controls how much gets fetched/cached and how far
                # LOCAL can zoom out.
                _world_radius = max(config.MAP_WORLD_RADIUS_M, city_radius * 1.15)
            elif _city_key is None:
                # No network for geocoding yet, and no prior city resolved --
                # degrade to a coordinate-keyed cache so MAP still works,
                # just without cross-visit city reuse until geocoding
                # eventually succeeds.
                _city_key = f"latlon_{geo_key[0]}_{geo_key[1]}"
            last_geo_key = geo_key

        fetch_radius = max(_local_radius, _world_radius, config.MAP_CITY_RADIUS_DEFAULT_M)
        age = osm.cache_age_s(_city_key)
        # Re-fetch on first sight of a city, or once the existing cache has
        # aged past its TTL -- this is "the API connection updates the
        # cache": a long-parked prop still periodically refreshes its
        # current city's data, it just usually short-circuits to a local
        # cache hit (age check) rather than hitting Overpass every tick.
        should_fetch = (_city_key != last_fetched_city) or age is None or age >= config.MAP_CACHE_MAX_AGE_S
        if should_fetch:
            area = osm.get_area(lat, lon, fetch_radius, _city_key)
            _last_area = area
            _last_center = (lat, lon)
            _fetched_radius_m = fetch_radius
            # A dense city block can be tens of thousands of road/building
            # segments -- drawing that is real work, so it happens here, off
            # the main thread, and only the finished Surfaces cross over.
            # Building a plain (non-display) pg.Surface off the main thread
            # is safe; only the queue hand-off below touches shared state.
            local_buffer = _render_map_buffer(area, lat, lon, _local_radius, important_only=False) if area else None
            world_buffer = _render_map_buffer(area, lat, lon, _world_radius, important_only=True) if area else None
            _result_queue.put((local_buffer, world_buffer))
            last_fetched_city = _city_key
        time.sleep(config.MAP_REFRESH_INTERVAL_S)


class _MapResultProcessor(esper.Processor):
    """Drains the worker thread's latest pre-rendered buffers (if any) once
    per frame -- all the actual drawing already happened on the worker
    thread, so this is just a cheap reference swap plus a Dirty flag."""

    def process(self, dt):
        latest = None
        while True:
            try:
                latest = _result_queue.get_nowait()
            except queue.Empty:
                break
        if latest is None:
            return
        global _local_buffer, _world_buffer, _local_center
        local_buffer, world_buffer = latest
        _local_buffer = local_buffer if local_buffer is not None else _render_no_signal_buffer()
        _world_buffer = world_buffer if world_buffer is not None else _render_no_signal_buffer()
        _local_center = _last_center
        _local_pan[0] = _local_pan[1] = 0.0
        _world_pan[0] = _world_pan[1] = 0.0
        _set_map_view(_local_entity, _local_buffer, _local_pan)
        _set_map_view(_world_entity, _world_buffer, _world_pan)
        _update_hover()
        _refresh_overlay()


class _CursorMoveProcessor(esper.Processor):
    """Smooth, dt-based cursor movement -- polls pg.key.get_pressed() every
    frame instead of going through the discrete, one-shot-per-keydown action
    system (see utils/settings.py's ACTIONS comment on why WASD isn't mapped
    there). Also polls the device's own live position every frame, so the
    "you are here" arrow updates smoothly between the map's own (much less
    frequent) data refreshes. Cursor movement is disabled entirely while
    typing a filter keyword, since that also involves holding down letter
    keys that happen to include w/a/s/d."""

    def process(self, dt):
        if registry.ACTIVE_LEAF not in (LOCAL_NODE_KEY, WORLD_NODE_KEY):
            return

        _poll_live_position()

        if _filter_mode:
            return
        keys = pg.key.get_pressed()
        dx = float(keys[pg.K_d]) - float(keys[pg.K_a])
        dy = float(keys[pg.K_s]) - float(keys[pg.K_w])
        if dx == 0.0 and dy == 0.0:
            return
        if dx and dy:
            dx *= 0.70710678
            dy *= 0.70710678
        _apply_movement(dx * _CURSOR_SPEED_PX_S * dt, dy * _CURSOR_SPEED_PX_S * dt)


def _poll_live_position():
    global _live_lat, _live_lon, _live_heading
    fix = location.get_location()
    if fix is None:
        return
    lat, lon, _source, heading = fix
    if lat == _live_lat and lon == _live_lon and heading == _live_heading:
        return
    _live_lat, _live_lon, _live_heading = lat, lon, heading
    _refresh_overlay()


def _set_map_view(entity, buffer, pan):
    esper.component_for_entity(entity, Renderable).image = _current_view(buffer, pan)
    esper.component_for_entity(entity, Dirty).state = 1


def _set_surface(entity, image):
    esper.component_for_entity(entity, Renderable).image = image
    esper.component_for_entity(entity, Dirty).state = 1


def _crop_rect(pan):
    x = int(round((_BUFFER_SIZE[0] - _VIEWPORT.width) / 2 + pan[0]))
    y = int(round((_BUFFER_SIZE[1] - _VIEWPORT.height) / 2 + pan[1]))
    x = max(0, min(_BUFFER_SIZE[0] - _VIEWPORT.width, x))
    y = max(0, min(_BUFFER_SIZE[1] - _VIEWPORT.height, y))
    return pg.Rect(x, y, _VIEWPORT.width, _VIEWPORT.height)


def _current_view(buffer, pan):
    return buffer.subsurface(_crop_rect(pan))


def _render_no_signal_buffer():
    image = pg.Surface(_BUFFER_SIZE)
    image.fill(theme.bg_color)
    font = ResourceLoader.get_font("MONOFONTO", 30)
    text = render_text(font, "NO SIGNAL", theme.draw_color, bg_color=theme.bg_color)
    image.blit(text, ((_BUFFER_SIZE[0] - text.get_width()) // 2, (_BUFFER_SIZE[1] - text.get_height()) // 2))
    return image


def _poi_icon(name):
    if name not in _icon_cache:
        raw = ResourceLoader.add_image(f"map_icon_{name}", f"images/mapmarkers/icon_map_{name}.png")
        _icon_cache[name] = fit_icon(raw, theme.draw_color, _POI_ICON_BOX)
    return _icon_cache[name]


def _player_icon(heading):
    """The "you are here + heading" marker -- deliberately a different shape
    (a directional arrow) from the WASD cursor's crosshair, since they mean
    different things: this is the device's real GPS position, the cursor is
    just where you're currently looking/hovering on screen. Rounds heading
    to the nearest 5 degrees so the small rotated-icon cache doesn't grow
    per exact degree."""
    heading_key = 0 if heading is None else int(round(heading / 5.0) * 5) % 360
    if heading_key not in _player_icon_cache:
        raw = ResourceLoader.add_image("map_icon_arrow", "images/mapmarkers/icon_arrow.png")
        fitted = fit_icon(raw, theme.draw_color, _PLAYER_ICON_BOX)
        # icon_arrow.png points up (north) at heading 0 -- pygame's rotate is
        # counter-clockwise for positive angles, so a clockwise compass
        # heading needs the sign flipped.
        _player_icon_cache[heading_key] = pg.transform.rotate(fitted, -heading_key)
    return _player_icon_cache[heading_key]


def _filtered_pois(pois, important_only=False):
    if important_only:
        pois = [poi for poi in pois if poi["icon"] in _WORLD_IMPORTANT_ICONS]

    keywords = [kw for kw in _filter_text.lower().replace(",", " ").split() if kw]
    if not keywords:
        return pois
    result = []
    for poi in pois:
        haystack = f"{poi.get('name', '')} {poi.get('icon', '')}".lower().replace("_", " ")
        if any(kw in haystack for kw in keywords):
            result.append(poi)
    return result


def _blend_toward_bg(fg_color, alpha):
    """Fakes a low-opacity draw color on this buffer's flat, opaque surface
    (no per-pixel alpha -- see _render_map_buffer's docstring) by blending
    it toward the background instead of drawing real translucency."""
    return tuple(bg + (fg - bg) * alpha for bg, fg in zip(theme.bg_color, fg_color))


def _zoom_fraction(radius_m):
    """0 at the most zoomed-in radius (_MIN_RADIUS_M), 1 at the most
    zoomed-out radius currently available (the last fetched radius) --
    drives the building fade so a wide view doesn't turn into a solid smear."""
    span = max(_fetched_radius_m - _MIN_RADIUS_M, 1.0)
    return max(0.0, min(1.0, (radius_m - _MIN_RADIUS_M) / span))


def _lerp(a, b, t):
    return a + (b - a) * t


def _render_map_buffer(area, center_lat, center_lon, radius_m, important_only):
    """Real OSM geometry (see game.modules.map.osm), projected with a flat
    equirectangular approximation -- accurate enough at the few-km scale a
    Pip-Boy map covers, far cheaper than a proper projection. Rendered at
    _BUFFER_SIZE (bigger than the viewport) so panning can crop a moving
    window out of it instead of re-rendering on every cursor move. The
    "you are here" arrow is NOT drawn here -- it lives on the cheap overlay
    layer instead, so it can move smoothly between buffer refreshes."""
    size = _BUFFER_SIZE
    image = pg.Surface(size)
    image.fill(theme.bg_color)
    scale = (min(size) / 2) / radius_m
    color = theme.draw_color
    water_color = tuple(c * 0.4 for c in color)
    zoom_t = _zoom_fraction(radius_m)
    building_fill_color = _blend_toward_bg(color, _lerp(_BUILDING_FILL_OPACITY_NEAR, _BUILDING_FILL_OPACITY_FAR, zoom_t))
    building_border_color = _blend_toward_bg(color, _lerp(_BUILDING_BORDER_OPACITY_NEAR, _BUILDING_BORDER_OPACITY_FAR, zoom_t))

    def _project(lat, lon):
        return project(lat, lon, center_lat, center_lon, scale, size)

    for poly in area["water"]:
        points = [_project(lat, lon) for lat, lon in poly]
        if len(points) >= 3:
            pg.draw.polygon(image, water_color, points)

    if not important_only:
        # Buildings are inherently street-level detail -- at WORLD's
        # whole-city scale they'd just be a solid smear, so they're skipped
        # entirely rather than filtered.
        for poly in area["buildings"]:
            points = [_project(lat, lon) for lat, lon in poly]
            if len(points) >= 3:
                pg.draw.polygon(image, building_fill_color, points)
            if len(points) >= 2:
                pg.draw.lines(image, building_border_color, False, points, 1)

    for road in area["roads"]:
        if important_only and road["highway"] not in _MAJOR_HIGHWAYS:
            continue
        points = [_project(lat, lon) for lat, lon in road["points"]]
        if len(points) >= 2:
            pg.draw.lines(image, color, False, points, 1 if important_only else 2)

    margin = _POI_ICON_BOX[0]
    for poi in _filtered_pois(area["pois"], important_only):
        x, y = _project(poi["lat"], poi["lon"])
        if -margin <= x <= size[0] + margin and -margin <= y <= size[1] + margin:
            icon = _poi_icon(poi["icon"])
            image.blit(icon, (x - icon.get_width() / 2, y - icon.get_height() / 2))

    return image


def _arrow_screen_pos():
    """Where the device's live position projects to on the currently active
    tab's screen -- using the active buffer's own render-time center/scale,
    same transform as hover hit-testing, then adjusted for the current pan."""
    radius_m, pan, _buffer, center = _active_state()
    if center is None or _live_lat is None:
        return None
    scale = (min(_BUFFER_SIZE) / 2) / radius_m
    lat0, lon0 = center
    bx, by = project(_live_lat, _live_lon, lat0, lon0, scale, _BUFFER_SIZE)
    crop = _crop_rect(pan)
    return (bx - crop.left, by - crop.top)


def _render_overlay():
    """The "you are here" arrow, cursor reticle, hover tooltip, and filter
    input box -- everything here is cheap to rebuild on every keypress or
    GPS tick, unlike the map buffer."""
    surf = pg.Surface(_VIEWPORT.size, pg.SRCALPHA)
    color = theme.draw_color

    arrow_pos = _arrow_screen_pos()
    if arrow_pos is not None:
        icon = _player_icon(_live_heading)
        surf.blit(icon, (arrow_pos[0] - icon.get_width() / 2, arrow_pos[1] - icon.get_height() / 2))

    # The cursor is deliberately a different shape (crosshair) from the
    # arrow above -- they mean different things (where you're looking vs.
    # where the device actually is).
    x, y = _cursor
    pg.draw.circle(surf, color, (x, y), 6, width=1)
    pg.draw.line(surf, color, (x - 10, y), (x + 10, y))
    pg.draw.line(surf, color, (x, y - 10), (x, y + 10))

    if _hovered_poi is not None:
        font = ResourceLoader.get_font("MONOFONTO", 12)
        label = (_hovered_poi.get("name") or _hovered_poi["icon"].replace("_", " ")).upper()
        text = render_text(font, label, color, bg_color=theme.bg_color)
        tx = min(x + 14, _VIEWPORT.width - text.get_width())
        ty = max(0, min(y - text.get_height() / 2, _VIEWPORT.height - text.get_height()))
        surf.blit(text, (tx, ty))

    if _filter_mode:
        font = ResourceLoader.get_font("MONOFONTO", 24)
        text = render_text(font, f"FILTER: {_filter_text}_", color, bg_color=theme.bg_color)
        surf.blit(text, (4, 4))

    return surf


def _refresh_overlay():
    entity = _local_overlay_entity if registry.ACTIVE_LEAF == LOCAL_NODE_KEY else _world_overlay_entity
    _set_surface(entity, _render_overlay())


def _is_world_active():
    return registry.ACTIVE_LEAF == WORLD_NODE_KEY


def _active_state():
    """(radius, pan, buffer, center) for whichever tab is currently active.
    WORLD always shows the original fetch center (the whole city at a
    glance); LOCAL's center can drift from it via panning/recentering."""
    if _is_world_active():
        return _world_radius, _world_pan, _world_buffer, _last_center
    return _local_radius, _local_pan, _local_buffer, _local_center


def _update_hover():
    global _hovered_poi
    _hovered_poi = None
    radius_m, pan, _buffer, center = _active_state()
    if _last_area is None or center is None:
        return
    scale = (min(_BUFFER_SIZE) / 2) / radius_m
    lat0, lon0 = center
    crop = _crop_rect(pan)
    best_dist = _HOVER_RADIUS_PX
    for poi in _filtered_pois(_last_area["pois"], important_only=_is_world_active()):
        bx, by = project(poi["lat"], poi["lon"], lat0, lon0, scale, _BUFFER_SIZE)
        x, y = bx - crop.left, by - crop.top
        dist = ((x - _cursor[0]) ** 2 + (y - _cursor[1]) ** 2) ** 0.5
        if dist <= best_dist:
            best_dist = dist
            _hovered_poi = poi


def _on_node_resumed(node_key):
    if node_key not in (LOCAL_NODE_KEY, WORLD_NODE_KEY):
        return
    global _cursor, _local_center, _local_buffer
    _cursor = [_VIEWPORT.width / 2, _VIEWPORT.height / 2]
    if node_key == LOCAL_NODE_KEY:
        # Snap back to the original fetch center on tab-away/tab-back rather
        # than preserving wherever panning/recentering had drifted to --
        # simplest predictable behavior, matching how zoom/pan already reset
        # on every other tab switch.
        if _last_area is not None and _last_center is not None and _local_center != _last_center:
            _local_center = _last_center
            _local_buffer = _render_map_buffer(_last_area, *_last_center, _local_radius, important_only=False)
        _local_pan[0] = _local_pan[1] = 0.0
        _set_map_view(_local_entity, _local_buffer, _local_pan)
    else:
        _world_pan[0] = _world_pan[1] = 0.0
        _set_map_view(_world_entity, _world_buffer, _world_pan)
    _update_hover()
    _refresh_overlay()


def _step_axis(cursor_val, pan_val, delta, dz_lo, dz_hi, viewport_extent, max_pan):
    """Moves `cursor_val` by `delta`. While the result stays inside the dead
    zone [dz_lo, dz_hi], only the cursor moves. Past that, `pan_val` absorbs
    the overflow (up to +/- max_pan) so the cursor visually pins at the dead
    zone edge while the world pans instead; once pan is maxed out, any
    further overflow moves the cursor again, capped at the true viewport
    edge -- a standard 2D dead-zone camera."""
    if delta == 0.0:
        return cursor_val, pan_val

    new_cursor = cursor_val + delta
    if dz_lo <= new_cursor <= dz_hi:
        return new_cursor, pan_val

    if new_cursor < dz_lo:
        overflow = dz_lo - new_cursor
        new_pan = max(-max_pan, pan_val - overflow)
        remaining = overflow - (pan_val - new_pan)
        return max(0.0, dz_lo - remaining), new_pan

    overflow = new_cursor - dz_hi
    new_pan = min(max_pan, pan_val + overflow)
    remaining = overflow - (new_pan - pan_val)
    return min(float(viewport_extent), dz_hi + remaining), new_pan


def _apply_movement(delta_x, delta_y):
    global _cursor
    _, pan, buffer, _center = _active_state()
    max_pan = _MAX_PAN

    new_x, new_pan_x = _step_axis(_cursor[0], pan[0], delta_x, _DEADZONE.left, _DEADZONE.right, _VIEWPORT.width, max_pan[0])
    new_y, new_pan_y = _step_axis(_cursor[1], pan[1], delta_y, _DEADZONE.top, _DEADZONE.bottom, _VIEWPORT.height, max_pan[1])

    _cursor[0], _cursor[1] = new_x, new_y
    pan[0], pan[1] = new_pan_x, new_pan_y

    if not _is_world_active():
        _recenter_local_if_needed()
        _, pan, buffer, _center = _active_state()

    entity = _world_entity if _is_world_active() else _local_entity
    _set_map_view(entity, buffer, pan)
    _update_hover()
    _refresh_overlay()


def _recenter_local_if_needed():
    """LOCAL-only: once panning has (nearly) hit the buffer's own edge,
    shift LOCAL's own view center by however far it panned and re-render
    from the already-cached city geometry -- no new Overpass fetch needed,
    since the city-sized fetch already covers far more than one buffer's
    worth of area. This is what actually lets WASD traverse the whole city
    at a comfortable street-level zoom instead of hard-stopping at a small
    patch around the original GPS fix."""
    global _local_center, _local_buffer

    if _last_area is None or _local_center is None:
        return
    if abs(_local_pan[0]) < _MAX_PAN[0] * _RECENTER_THRESHOLD and abs(_local_pan[1]) < _MAX_PAN[1] * _RECENTER_THRESHOLD:
        return

    scale = (min(_BUFFER_SIZE) / 2) / _local_radius
    lat0, lon0 = _local_center
    new_lon = lon0 + (_local_pan[0] / scale) / geo.meters_per_deg_lon(lat0)
    new_lat = lat0 - (_local_pan[1] / scale) / geo.METERS_PER_DEG_LAT

    _local_center = (new_lat, new_lon)
    _local_buffer = _render_map_buffer(_last_area, new_lat, new_lon, _local_radius, important_only=False)
    _local_pan[0] = _local_pan[1] = 0.0


def _clamp_radius(radius, zoom_in):
    new_radius = radius / _ZOOM_FACTOR if zoom_in else radius * _ZOOM_FACTOR
    # Can't zoom out past what was actually fetched -- there's no geometry
    # beyond the last Overpass query's own radius to show.
    return max(_MIN_RADIUS_M, min(_fetched_radius_m, new_radius))


def _zoom(zoom_in: bool):
    global _local_radius, _world_radius, _local_buffer, _world_buffer
    is_world = _is_world_active()
    if is_world:
        _world_radius = _clamp_radius(_world_radius, zoom_in)
        radius = _world_radius
        center = _last_center
    else:
        _local_radius = _clamp_radius(_local_radius, zoom_in)
        radius = _local_radius
        center = _local_center

    if _last_area is not None and center is not None:
        buffer = _render_map_buffer(_last_area, *center, radius, important_only=is_world)
        if is_world:
            _world_buffer = buffer
            _world_pan[0] = _world_pan[1] = 0.0
            _set_map_view(_world_entity, _world_buffer, _world_pan)
        else:
            _local_buffer = buffer
            _local_pan[0] = _local_pan[1] = 0.0
            _set_map_view(_local_entity, _local_buffer, _local_pan)
    _update_hover()
    _refresh_overlay()


def _enter_filter_mode():
    global _filter_mode
    _filter_mode = True
    registry.set_text_input_active(True)
    _refresh_overlay()


def _apply_filter():
    global _local_buffer, _world_buffer
    if _last_area is not None and _local_center is not None:
        _local_buffer = _render_map_buffer(_last_area, *_local_center, _local_radius, important_only=False)
        _world_buffer = _render_map_buffer(_last_area, *_last_center, _world_radius, important_only=True)
        _set_map_view(_local_entity, _local_buffer, _local_pan)
        _set_map_view(_world_entity, _world_buffer, _world_pan)
    _update_hover()
    _refresh_overlay()


def _on_map_action(action):
    if registry.ACTIVE_LEAF not in (LOCAL_NODE_KEY, WORLD_NODE_KEY):
        return
    if action == "map_filter":
        _enter_filter_mode()
    elif action in ("dial_up", "dial_down"):
        _zoom(zoom_in=(action == "dial_up"))


def _on_key_text(event):
    """Only ever called while registry.TEXT_INPUT_ACTIVE is True, which only
    MAP's filter currently turns on -- see _enter_filter_mode()."""
    global _filter_mode, _filter_text
    if not _filter_mode:
        return

    if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
        _filter_mode = False
        registry.set_text_input_active(False)
        _apply_filter()
    elif event.key == pg.K_ESCAPE:
        _filter_text = ""
        _filter_mode = False
        registry.set_text_input_active(False)
        _apply_filter()
    elif event.key == pg.K_BACKSPACE:
        _filter_text = _filter_text[:-1]
        _refresh_overlay()
    elif event.unicode and event.unicode.isprintable():
        _filter_text += event.unicode
        _refresh_overlay()


class _ClockFooterProcessor(esper.Processor):
    """Ports the old Map.update() override: keeps LOCAL's footer date/time
    live while it's on screen. Priority 32 so it runs before UIRenderProcessor
    (30) in the same frame -- otherwise a section change wouldn't be picked up
    until the following frame."""

    def __init__(self, footer_ent):
        self.footer_ent = footer_ent

    def process(self, dt):
        if not esper.has_component(self.footer_ent, Active):
            return
        state = esper.component_for_entity(self.footer_ent, FooterState)
        now = datetime.now()
        changed_date = state.update_section(0, now.strftime("%d.%m.%Y"))
        changed_time = state.update_section(1, now.strftime("%H:%M:%S"))
        if changed_date or changed_time:
            esper.component_for_entity(self.footer_ent, Dirty).state = 1
