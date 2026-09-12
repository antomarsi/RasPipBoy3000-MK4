"""Checks a free, community-run online radio directory (radio-browser.info,
no API key needed) for currently-online stations, so RADIO isn't limited to
the shipped/user-defined station list. `hidebroken=true` asks the directory
itself for only stations its own checker last verified as actually
reachable -- this is "the radio checking for online radios", not just a
fixed list of URLs that may or may not still work.

Ordering by global click count (no country filter) skews heavily toward a
handful of huge European broadcasters -- confirmed by hand: an unfiltered
query returns mostly French/UK stations, while `countrycode=US` returns an
all-US top-8. `RADIO_ONLINE_COUNTRY` (utils/settings.py, unset by default)
lets that be tuned per-device instead of guessing a "better" global default.

Cached to disk (like MAP's OSM data) both to be a polite API citizen and so
the list survives being offline after the first successful check.
"""
import json
import os
import time
from typing import Optional

import requests

from utils.logger import logger
from utils.settings import config

_API_URL = "https://de1.api.radio-browser.info/json/stations/search"
_HEADERS = {"User-Agent": "RasPipBoy3000-MK4/1.0 (cosplay prop; personal use)"}


def _cache_path() -> str:
    # Keyed by country filter too -- switching RADIO_ONLINE_COUNTRY shouldn't
    # reuse a list fetched under a different (or no) filter.
    country = config.RADIO_ONLINE_COUNTRY or "global"
    return os.path.join(config.RADIO_CACHE_DIR, f"directory_{country.lower()}.json")


def get_online_stations(limit: int) -> Optional[list]:
    """Up to `limit` currently-online, popular stations as
    {"name", "url", "tags", "country"} dicts, optionally restricted to
    RADIO_ONLINE_COUNTRY. Prefers a fresh disk cache over hitting the API;
    falls back to a stale cache (or None, if there's never been a
    successful check) when the API is unreachable."""
    if limit <= 0:
        return None

    path = _cache_path()
    if _cache_fresh(path):
        cached = _load_cache(path)
        if cached:
            return cached[:limit]

    stations = _fetch(limit)
    if stations is not None:
        _save_cache(path, stations)
        return stations

    cached = _load_cache(path)
    return cached[:limit] if cached else None


def _cache_fresh(path: str) -> bool:
    if not os.path.exists(path):
        return False
    return time.time() - os.path.getmtime(path) < config.RADIO_DIRECTORY_CACHE_MAX_AGE_S


def _fetch(limit: int) -> Optional[list]:
    try:
        params = {"limit": limit, "order": "clickcount", "reverse": "true", "hidebroken": "true"}
        if config.RADIO_ONLINE_COUNTRY:
            params["countrycode"] = config.RADIO_ONLINE_COUNTRY
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
                "name": name, "url": url,
                "tags": entry.get("tags", ""), "country": entry.get("countrycode", ""),
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
