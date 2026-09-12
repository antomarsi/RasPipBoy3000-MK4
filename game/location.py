"""Background location service: GPS when the hardware is present, IP-based
geolocation otherwise (desktop dev, or a Pi with no GPS module wired up).

Mirrors game/pipboy.py's GPIO pattern -- a background thread does the slow
part (serial reads, HTTP calls) and only ever swaps a plain module-level
variable; the main thread only ever reads it via get_location(), never
touches pyserial/requests directly. Swapping the whole tuple atomically
(rather than mutating fields) is what keeps that read race-free without a
lock, same reasoning as PipBoy.action_queue.
"""

import threading
import time
from typing import Optional, Tuple

import requests

from game.geo import bearing_deg, flat_distance_m
from utils.logger import logger
from utils.settings import config

# (lat, lon, source, heading) -- source is "gps" or "ip"; heading is a
# compass bearing in degrees (0=north), or None if never established.
# None until the first fix.
_location: Optional[Tuple[float, float, str, Optional[float]]] = None
_thread: Optional[threading.Thread] = None

# A GPS fix's own course-over-ground is preferred when available; otherwise
# heading is derived from movement between consecutive fixes, and held
# steady (not reset) when the device is stationary -- an occasional GPS/IP
# jitter of a few meters shouldn't spin the map's arrow around.
_last_fix_position: Optional[Tuple[float, float]] = None
_last_heading: Optional[float] = None
_MIN_MOVEMENT_FOR_HEADING_M = 5.0

GPS_FIX_TIMEOUT_S = 3.0
IP_GEO_REFRESH_S = 300.0  # IP-based location is city-level and network-cheap
                          # to skip re-checking as often as GPS


def get_location() -> Optional[Tuple[float, float, str, Optional[float]]]:
    return _location


def init():
    global _thread
    if _thread is not None:
        return
    _thread = threading.Thread(target=_run, daemon=True)
    _thread.start()


def _run():
    last_ip_check = 0.0
    while True:
        fix = _read_gps() if config.GPS_AVAILABLE else None
        if fix is None:
            now = time.monotonic()
            if now - last_ip_check >= IP_GEO_REFRESH_S:
                last_ip_check = now
                fix = _read_ip_geo()
        if fix is not None:
            lat, lon, source, heading = fix
            if heading is None:
                heading = _derive_heading(lat, lon)
            _set_location((lat, lon, source, heading))
        # GPS hardware (when present) is worth polling much faster than the
        # heavy MAP-tab Overpass refresh cadence -- a worn, walking prop
        # should update its position/heading every couple seconds, not every
        # couple minutes.
        time.sleep(GPS_FIX_TIMEOUT_S if config.GPS_AVAILABLE else config.GPS_POLL_INTERVAL_S)


def _set_location(fix: Tuple[float, float, str, Optional[float]]):
    global _location
    _location = fix


def _derive_heading(lat: float, lon: float) -> Optional[float]:
    global _last_fix_position, _last_heading
    if _last_fix_position is not None:
        prev_lat, prev_lon = _last_fix_position
        if flat_distance_m(prev_lat, prev_lon, lat, lon) >= _MIN_MOVEMENT_FOR_HEADING_M:
            _last_heading = bearing_deg(prev_lat, prev_lon, lat, lon)
    _last_fix_position = (lat, lon)
    return _last_heading


def _read_gps() -> Optional[Tuple[float, float, str, Optional[float]]]:
    import serial  # type: ignore
    import pynmea2  # type: ignore

    try:
        with serial.Serial(config.GPS_SERIAL_PORT, config.GPS_BAUDRATE, timeout=1) as port:
            deadline = time.monotonic() + GPS_FIX_TIMEOUT_S
            while time.monotonic() < deadline:
                line = port.readline().decode("ascii", errors="ignore").strip()
                if not line.startswith(("$GPGGA", "$GPRMC", "$GNGGA", "$GNRMC")):
                    continue
                try:
                    msg = pynmea2.parse(line)
                except pynmea2.ParseError:
                    continue
                if getattr(msg, "latitude", 0) and getattr(msg, "longitude", 0):
                    # Only RMC carries course-over-ground, and only while the
                    # receiver considers the fix moving/valid -- absent or
                    # empty otherwise, in which case _derive_heading() below
                    # takes over.
                    course = getattr(msg, "true_course", None)
                    heading = float(course) if course not in (None, "") else None
                    return (msg.latitude, msg.longitude, "gps", heading)
    except (OSError, serial.SerialException) as exc:
        logger.debug(f"GPS read failed: {exc}")
    return None


def _read_ip_geo() -> Optional[Tuple[float, float, str, Optional[float]]]:
    try:
        response = requests.get(config.IP_GEO_URL, timeout=5)
        data = response.json()
        if data.get("status") == "fail":
            return None
        return (data["lat"], data["lon"], "ip", None)
    except (requests.RequestException, KeyError, ValueError) as exc:
        logger.debug(f"IP geolocation failed: {exc}")
        return None
