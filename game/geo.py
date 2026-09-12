"""Small flat-earth geo helpers shared by MAP's rendering, city geocoding,
and live-heading calculation -- all operate at street/city scale, where a
flat equirectangular approximation is far cheaper than a true haversine and
well within acceptable error (a fraction of a percent under ~50km)."""
import math

METERS_PER_DEG_LAT = 111_320.0


def meters_per_deg_lon(at_lat: float) -> float:
    return METERS_PER_DEG_LAT * math.cos(math.radians(at_lat))


def project(lat, lon, center_lat, center_lon, scale, size):
    """(lat, lon) -> pixel position on a `size`-sized surface centered on
    (center_lat, center_lon) at `scale` pixels per meter."""
    dx = (lon - center_lon) * meters_per_deg_lon(center_lat)
    dy = (lat - center_lat) * METERS_PER_DEG_LAT
    return (size[0] / 2 + dx * scale, size[1] / 2 - dy * scale)


def flat_distance_m(lat1, lon1, lat2, lon2) -> float:
    dx = (lon2 - lon1) * meters_per_deg_lon(lat1)
    dy = (lat2 - lat1) * METERS_PER_DEG_LAT
    return math.hypot(dx, dy)


def bearing_deg(lat1, lon1, lat2, lon2) -> float:
    """Compass bearing in degrees (0=north, 90=east, ...) from point 1 to
    point 2 -- used to derive the map's heading arrow when the GPS fix
    itself doesn't report a course (e.g. IP geolocation, or a GPS fix with
    no course-over-ground field)."""
    dx = (lon2 - lon1) * meters_per_deg_lon(lat1)
    dy = (lat2 - lat1) * METERS_PER_DEG_LAT
    return math.degrees(math.atan2(dx, dy)) % 360.0
