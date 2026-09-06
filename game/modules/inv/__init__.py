from core.components import Dirty, Layer, Position, Renderable
from game.data import catalog
from game.data.store import INVENTORY_CATEGORIES, save_data
from game.modules.registry import create_node
from game.ui import UI_MARGIN, MenuState

# category -> its catalog dict (baseid -> item). No per-item right panel or
# weight/caps totals yet -- title-only lists, see the plan's "Explicitly out
# of scope" section.
CATALOGS = {
    "weapons": catalog.weapons,
    "apparel": catalog.apparel,
    "aid": catalog.aid,
    "misc": catalog.misc,
    "junk": catalog.junk,
    "mods": catalog.mods,
    "ammo": catalog.ammo,
}


def register(pipboy):
    create_node("inv", "INV")
    for category in INVENTORY_CATEGORIES:
        _register_category(category)


def _register_category(category):
    owned_items = save_data.inventory.get(category, [])
    catalog_map = CATALOGS[category]
    titles = [catalog_map[item.baseid]["title"] for item in owned_items if item.baseid in catalog_map]
    create_node(f"inv.{category}", category.upper(), parent="inv", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=titles),
    ])
