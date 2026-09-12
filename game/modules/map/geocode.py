"""Resolves a GPS/IP fix to "which city is this" so MAP can cache per city
instead of per small patch of coordinates -- the same city should reuse one
cache file regardless of exactly where within it the device sits, and
revisiting a previously-seen city (after being elsewhere) should hit that
city's existing cache again rather than starting over.

Uses Nominatim, OpenStreetMap's free reverse-geocoding service (same
provider family as game.modules.map.osm's Overpass API).
"""
import requests

from game.geo import flat_distance_m
from utils.logger import logger
from utils.settings import config

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
# Nominatim's usage policy requires a real identifying User-Agent and caps
# unattended use at roughly 1 request/second -- both trivially satisfied
# here, since this only re-geocodes when the device has moved to a new
# ~1km cell (see game/modules/map/__init__.py's worker loop).
_HEADERS = {"User-Agent": "RasPipBoy3000-MK4/1.0 (cosplay prop; personal use)"}

# The device's last resolved (country_code, state) as an ISO-3166-1 alpha-2
# code + region/state name, e.g. ("br", "Santa Catarina") -- a side effect of
# reverse_geocode() below, kept module-level so other code (RADIO's online
# directory search) can reuse whatever MAP already resolved instead of
# making its own Nominatim call. None until the first successful lookup.
_last_region = None


def get_last_region():
    """Returns the last (country_code, state) resolved by reverse_geocode(),
    or None if no lookup has succeeded yet. country_code is lowercase ISO
    3166-1 alpha-2 (e.g. "br"); state may be None if the address had none."""
    return _last_region


def reverse_geocode(lat: float, lon: float):
    """Returns (city_key, radius_m) for the city/town containing (lat, lon),
    or None if the lookup failed (offline, Nominatim unreachable, no result).
    city_key is a filesystem-safe identifier stable for that city across
    visits; radius_m is sized to the resolved area's own bounding box (a
    big metro area gets a bigger fetch than a small town), clamped to a
    sane range so a huge city doesn't produce an unfetchable Overpass query."""
    global _last_region
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"format": "jsonv2", "lat": lat, "lon": lon, "zoom": 10, "addressdetails": 1},
            headers=_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.debug(f"Reverse geocode failed: {exc}")
        return None

    address = data.get("address", {})
    city = (address.get("city") or address.get("town") or address.get("village")
            or address.get("municipality") or data.get("name"))
    if not city:
        return None

    country = address.get("country_code", "")
    _last_region = (country, address.get("state"))
    city_key = f"{city}_{country}".lower().replace(" ", "_")
    radius_m = _radius_from_bbox(data.get("boundingbox"), lat, lon)
    return city_key, radius_m


def _radius_from_bbox(boundingbox, lat, lon) -> float:
    if not boundingbox or len(boundingbox) != 4:
        return config.MAP_CITY_RADIUS_DEFAULT_M
    south, north, west, east = (float(v) for v in boundingbox)
    radius = max(
        flat_distance_m(lat, lon, north, east),
        flat_distance_m(lat, lon, south, west),
        flat_distance_m(lat, lon, north, west),
        flat_distance_m(lat, lon, south, east),
    )
    return max(config.MAP_CITY_RADIUS_MIN_M, min(config.MAP_CITY_RADIUS_MAX_M, radius))
