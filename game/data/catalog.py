import json
from pathlib import Path

from utils.settings import config
from utils.logger import logger

_DATA_DIR = Path(config.ASSETS_FOLDER) / "data"


def _load_json(filename: str):
    with open(_DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def _index_by_baseid(items: list) -> dict:
    return {item["baseid"]: item for item in items}


weapons: dict = _index_by_baseid(_load_json("weapons.json"))
apparel: dict = _index_by_baseid(_load_json("apparel.json"))
aid: dict = _index_by_baseid(_load_json("aid.json"))
ammo: dict = _index_by_baseid(_load_json("ammo.json"))
junk: dict = _index_by_baseid(_load_json("junk.json"))
mods: dict = _index_by_baseid(_load_json("mods.json"))
misc: dict = _index_by_baseid(_load_json("misc.json"))
perks: dict = _index_by_baseid(_load_json("perks.json"))

# special.json is keyed by SPECIAL stat name (e.g. "Strength"), not baseid.
special: dict = _load_json("special.json")

# categories.json is keyed by INV category name (e.g. "weapons") and defines
# which fields from that category's own catalog to show in a right-panel
# stat table, in order, with display labels -- see game/modules/inv/.
categories: dict = _load_json("categories.json")

# map_categories.json maps OSM tag (key -> value) onto a MAP marker icon
# name -- see game/modules/map/osm.py.
map_categories: dict = _load_json("map_categories.json")

# radio_profiles.json defines RADIO's distortion profiles (ffmpeg audio
# filter chains) -- see game/modules/radio/playback.py.
radio_profiles: dict = _load_json("radio_profiles.json")

logger.debug(
    f"Catalog loaded: {len(weapons)} weapons, {len(apparel)} apparel, {len(aid)} aid, "
    f"{len(ammo)} ammo, {len(junk)} junk, {len(mods)} mods, {len(misc)} misc, {len(perks)} perks"
)
