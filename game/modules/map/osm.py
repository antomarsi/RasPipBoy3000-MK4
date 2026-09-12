"""Real map geometry, sourced from OpenStreetMap's free Overpass API.

Deliberately pulls raw vector geometry (roads/buildings/water/POIs as lat/lon
point lists) rather than raster map tiles -- there's no way to reskin a PNG
tile server's output into the Pip-Boy's green wireframe look, but drawing
plain lines/polygons ourselves in game.ui's theme color is exactly what the
rest of this app already does. This also keeps the on-device memory/CPU cost
far lower than a raster-tile pipeline, which matters on the Pi Zero 2 W.

Runs entirely off the main thread (see game/modules/map/__init__.py's worker)
-- Overpass queries can take several seconds.
"""

import json
import math
import os
import time
from typing import Optional

import requests

from game.data import catalog
from utils.logger import logger
from utils.settings import config

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# The public Overpass instance's Apache config 406s any request without a
# real Accept header and rejects the default python-requests User-Agent as
# likely-abusive traffic -- confirmed by hand against the live server.
_HEADERS = {"User-Agent": "RasPipBoy3000-MK4/1.0 (cosplay prop; personal use)", "Accept": "*/*"}

# OSM tag keys queried as POI nodes and consulted (in this order) for an icon
# -- see assets/data/map_categories.json for the actual key -> value -> icon
# mapping (user-editable; not every OSM category has a good fit in the
# current Fallout-styled marker set).
_POI_TAG_KEYS = (
    "amenity", "shop", "tourism", "leisure", "natural",
    "historic", "railway", "public_transport", "military",
)


def poi_icon(tags: dict) -> str:
    categories = catalog.map_categories
    for key in _POI_TAG_KEYS:
        value = tags.get(key)
        if value is None:
            continue
        key_map = categories.get(key)
        if not key_map:
            continue
        icon = key_map.get(value) or key_map.get("_default")
        if icon:
            return icon
    return categories.get("_default", "undiscovered")


def _build_query(lat: float, lon: float, radius_m: float) -> str:
    around = f"(around:{radius_m},{lat},{lon})"
    clauses = "".join(
        f'{kind}["{tag}"]{around};\n'
        for kind, tag in (
            ("way", "highway"), ("way", "building"),
            ("way", "natural"), ("way", "landuse"),
        )
    ) + "".join(
        f'node["{tag}"]{around};\n' for tag in _POI_TAG_KEYS
    )
    return f"[out:json][timeout:25];\n(\n{clauses}\n);\nout geom;"


def _fetch_overpass(lat: float, lon: float, radius_m: float) -> Optional[dict]:
    try:
        response = requests.post(
            OVERPASS_URL, data={"data": _build_query(lat, lon, radius_m)},
            headers=_HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.debug(f"Overpass fetch failed: {exc}")
        return None


def _parse(raw: dict) -> dict:
    roads, buildings, water, pois = [], [], [], []
    for el in raw.get("elements", []):
        tags = el.get("tags", {})
        if el["type"] == "way":
            points = [(pt["lat"], pt["lon"]) for pt in el.get("geometry", []) if pt]
            if not points:
                continue
            if "highway" in tags:
                # highway kept alongside the geometry so a wide-area render
                # (WORLD) can show only major roads instead of every alley --
                # see __init__.py's _MAJOR_HIGHWAYS.
                roads.append({"points": points, "highway": tags["highway"]})
            elif "building" in tags:
                buildings.append(points)
            elif tags.get("natural") == "water" or tags.get("landuse") == "reservoir":
                water.append(points)
        elif el["type"] == "node" and any(tag in tags for tag in _POI_TAG_KEYS):
            pois.append({
                "lat": el["lat"], "lon": el["lon"],
                "icon": poi_icon(tags), "name": tags.get("name", ""),
            })
    return {"roads": roads, "buildings": buildings, "water": water, "pois": pois}


def _cache_path(cache_key: str) -> str:
    return os.path.join(config.MAP_CACHE_DIR, f"{cache_key}.json")


def cache_age_s(cache_key: str) -> Optional[float]:
    """Seconds since `cache_key`'s cache file was last written, or None if it
    doesn't exist yet. Lets a caller decide whether a fetch is worth doing
    at all before committing to the (network-bound) get_area() call."""
    path = _cache_path(cache_key)
    if not os.path.exists(path):
        return None
    return time.time() - os.path.getmtime(path)


def get_area(lat: float, lon: float, radius_m: float, cache_key: str) -> Optional[dict]:
    """Real vector geometry around (lat, lon), preferring a fresh cache hit,
    then a live Overpass fetch, then a stale cache as a last resort (so a
    prop with no signal still shows the last-known area instead of nothing).
    Returns None only when there is truly no data available yet.

    `cache_key` identifies *what* is being cached (typically a city name --
    see game/modules/map/geocode.py) rather than being derived from the
    coordinates here, so the same city reuses one cache file no matter where
    within it the fix landed, and a previously-visited city's cache survives
    visiting other cities in between."""
    os.makedirs(config.MAP_CACHE_DIR, exist_ok=True)
    path = _cache_path(cache_key)
    age = cache_age_s(cache_key)

    if age is not None and age < config.MAP_CACHE_MAX_AGE_S:
        return _load_cache(path)

    raw = _fetch_overpass(lat, lon, radius_m)
    if raw is not None:
        area = _parse(raw)
        try:
            with open(path, "w") as f:
                json.dump(area, f)
        except OSError as exc:
            logger.debug(f"Failed to write map cache: {exc}")
        return area

    if age is not None:
        return _load_cache(path)
    return None


def _load_cache(path: str) -> Optional[dict]:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        logger.debug(f"Failed to read map cache: {exc}")
        return None
