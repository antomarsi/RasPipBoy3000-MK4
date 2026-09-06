import esper

from core.components import Active, Dirty, Layer, Position, Renderable, Running
from game.modules.registry import create_node
from game.ui import UI_MARGIN, MenuState
from utils.logger import logger
from utils.settings import config

NODE_KEY = "radio"
STATIONS_NODE_KEY = "radio.stations"


def register(pipboy):
    stations = list(config.RADIOS.keys())
    node_ent = create_node(NODE_KEY, "RADIO", background=True)
    menu_ent = create_node(STATIONS_NODE_KEY, "", parent=NODE_KEY, background=True, components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=stations, max_items=9),
    ])
    esper.add_processor(_RadioTickProcessor(node_ent, menu_ent), priority=10)


class _RadioTickProcessor(esper.Processor):
    """Proves the background mechanism: RADIO is `background=True`, so it
    keeps its `Running` tag (and this keeps ticking) even while another tab
    is Active. Logs the current "station" every 5s -- no real audio, see the
    plan's "Explicitly out of scope" section."""

    def __init__(self, node_ent, menu_ent):
        self.node_ent = node_ent
        self.menu_ent = menu_ent
        self._elapsed = 0.0

    def process(self, dt):
        if not esper.has_component(self.node_ent, Running):
            return
        self._elapsed += dt
        if self._elapsed < 5.0:
            return
        self._elapsed = 0.0

        menu_state = esper.component_for_entity(self.menu_ent, MenuState)
        station = menu_state.items[menu_state.selected] if menu_state.items else "(no station)"
        in_background = not esper.has_component(self.node_ent, Active)
        logger.debug(f"[RADIO] now playing: {station} (backgrounded: {in_background})")
