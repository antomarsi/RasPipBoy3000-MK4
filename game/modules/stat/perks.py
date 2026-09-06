from core.components import Dirty, Layer, Position, Renderable
from game.data.catalog import perks as perks_catalog
from game.data.store import save_data
from game.modules.registry import create_node
from game.ui import UI_MARGIN, MenuState

NODE_KEY = "stat.perks"


def register(pipboy):
    titles = [perks_catalog[p["baseid"]]["title"] for p in save_data.perks if p["baseid"] in perks_catalog]
    create_node(NODE_KEY, "PERKS", parent="stat", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=titles),
    ])
