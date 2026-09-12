"""MAP's OSM-tag-to-marker-icon rules (assets/data/map_categories.json --
see game/data/catalog.py and game/modules/map/osm.py), documented here
instead of a "_comment" field in the JSON itself."""
from typing import Optional

from pydantic import BaseModel, Field


class MapCategoryRules(BaseModel):
    """Icon rules for one OSM tag key (e.g. "amenity"). `values` maps a tag
    VALUE (e.g. "restaurant") to a marker icon name -- a file under
    assets/images/mapmarkers/icon_map_<name>.png -- or null when nothing in
    the current (Fallout-wasteland-styled) icon set fits well; map it by
    hand once you've decided, or add a new icon file and reference it here.
    `default` applies to any value of this tag key not listed in `values`
    at all."""
    values: dict[str, Optional[str]] = Field(default_factory=dict)
    default: Optional[str] = None


class MapCategories(BaseModel):
    """The full OSM tag -> marker icon rule set. `categories` is keyed by
    OSM tag (e.g. "amenity", "shop", "natural"). `default` is the last-
    resort fallback icon when no tag key/value in `categories` matched at
    all."""
    categories: dict[str, MapCategoryRules] = Field(default_factory=dict)
    default: str = "undiscovered"
