"""Checks a free, community-run online radio directory (radio-browser.info,
no API key needed) for currently-online stations, so RADIO isn't limited to
the shipped/user-defined station list. `hidebroken=true` asks the directory
itself for only stations its own checker last verified as actually
reachable -- this is "the radio checking for online radios", not just a
fixed list of URLs that may or may not still work.

Two independent scopes are fetched, matching RADIO's LOCAL SIGNAL / GLOBAL
SIGNAL bands:
- "global": no country/state filter at all, ordered by raw click count.
  Confirmed by hand: this skews heavily toward a handful of huge
  broadcasters (the US's iHeartRadio network, French/UK stations) -- a
  worldwide "most popular" chart, not a neutral sample.
- "local": filtered to the device's own region. `RADIO_ONLINE_COUNTRY`
  (utils/settings.py, unset by default) can pin this to one country
  manually; when unset, the device's own GPS/IP-resolved location is used
  instead (see `_auto_region()`) -- MAP already reverse-geocodes that
  location for its own caching, so this reuses that result
  (`game.modules.map.geocode`) rather than making a second Nominatim call.

Each returned station also carries the directory's own `country`/`state`
fields (full country name + region, e.g. "Brazil"/"Santa Catarina CA") --
these come straight from radio-browser.info's own station metadata, so no
country-code-to-name lookup of our own is needed for RADIO's "which country
is this from" description text.

Cached to disk (like MAP's OSM data) both to be a polite API citizen and so
the list survives being offline after the first successful check.
"""
import json
import os
import time
from typing import Optional

import requests

from game.modules.map import geocode
from utils.logger import logger
from utils.settings import config

_API_URL = "https://de1.api.radio-browser.info/json/stations/search"
_HEADERS = {"User-Agent": "RasPipBoy3000-MK4/1.0 (cosplay prop; personal use)"}


def _auto_region():
    """Returns (country_code, state) from the device's own last-resolved
    location, or (None, None) if MAP hasn't geocoded a fix yet (e.g. still
    offline early in boot)."""
    region = geocode.get_last_region()
    return region if region else (None, None)


def _resolve_filter(scope: str):
    """Returns (countrycode, state) to filter the directory search by.
    "global" is always unfiltered (a worldwide chart, regardless of any
    local config) -- filtering it would just make it a second copy of
    "local". "local" prefers a manually configured RADIO_ONLINE_COUNTRY,
    then the device's own resolved location, then no filter at all if
    neither is available yet."""
    if scope == "global":
        return None, None
    if config.RADIO_ONLINE_COUNTRY:
        return config.RADIO_ONLINE_COUNTRY, None
    return _auto_region()


def _cache_path(scope: str) -> str:
    # Keyed by scope + country/state -- a different resolved/manual filter
    # (or the global/local split itself) shouldn't reuse a list fetched
    # under different conditions.
    country, state = _resolve_filter(scope)
    key = f"{country}_{state}" if state else (country or "unfiltered")
    return os.path.join(config.RADIO_CACHE_DIR, f"directory_{scope}_{key.lower().replace(' ', '_')}.json")


def get_online_stations(limit: int, scope: str = "local") -> Optional[list]:
    """Up to `limit` currently-online, popular stations as
    {"name", "url", "tags", "country", "countrycode", "state"} dicts.
    scope="local" restricts to the device's own region (see
    `_resolve_filter`); scope="global" is always an unfiltered worldwide
    chart. Prefers a fresh disk cache over hitting the API; falls back to a
    stale cache (or None, if there's never been a successful check) when
    the API is unreachable."""
    if limit <= 0:
        return None

    path = _cache_path(scope)
    if _cache_fresh(path):
        cached = _load_cache(path)
        if cached:
            return cached[:limit]

    stations = _fetch(limit, scope)
    if stations is not None:
        _save_cache(path, stations)
        return stations

    cached = _load_cache(path)
    return cached[:limit] if cached else None


def _cache_fresh(path: str) -> bool:
    if not os.path.exists(path):
        return False
    return time.time() - os.path.getmtime(path) < config.RADIO_DIRECTORY_CACHE_MAX_AGE_S


def _fetch(limit: int, scope: str) -> Optional[list]:
    try:
        params = {"limit": limit, "order": "clickcount", "reverse": "true", "hidebroken": "true"}
        country, state = _resolve_filter(scope)
        if country:
            params["countrycode"] = country
        if state:
            params["state"] = state
        response = requests.get(_API_URL, params=params, headers=_HEADERS, timeout=15)
        response.raise_for_status()
        raw = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.debug(f"Radio online directory check failed: {exc}")
        return None

    stations = []
    for entry in raw:
        url = entry.get("url_resolved") or entry.get("url")
        name = (entry.get("name") or "").strip()
        if url and name:
            stations.append({
                "name": name, "url": url, "tags": entry.get("tags", ""),
                "country": entry.get("country", ""), "countrycode": entry.get("countrycode", ""),
                "state": entry.get("state", ""),
            })
    return stations


def _load_cache(path: str) -> Optional[list]:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        logger.debug(f"Failed to read radio directory cache: {exc}")
        return None


def _save_cache(path: str, stations: list):
    os.makedirs(config.RADIO_CACHE_DIR, exist_ok=True)
    try:
        with open(path, "w") as f:
            json.dump(stations, f)
    except OSError as exc:
        logger.debug(f"Failed to write radio directory cache: {exc}")
