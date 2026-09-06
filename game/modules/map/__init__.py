from datetime import datetime

import esper

from core.components import Active, Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data.store import theme
from game.modules.registry import create_node
from game.ui import UI_MARGIN, FooterState, render_text
from utils.settings import config

LOCAL_NODE_KEY = "map.local"


def register(pipboy):
    create_node("map", "MAP")
    create_node(LOCAL_NODE_KEY, "LOCAL", parent="map")
    create_node("map.world", "WORLD", parent="map")

    _register_local_footer()
    _register_world_placeholder()


def _register_local_footer():
    footer_state = FooterState(sections=["", "", ("LOCAL MAP", 2)])
    footer_ent = esper.create_entity(
        Position(UI_MARGIN, config.HEIGHT - 45), Renderable(), Layer(5), Dirty(1),
        footer_state, OwnedBy(LOCAL_NODE_KEY))
    esper.add_processor(_ClockFooterProcessor(footer_ent), priority=32)


def _register_world_placeholder():
    font = ResourceLoader.get_font("MONOFONTO", 30)
    image = render_text(font, "WORLD MAP", theme.draw_color)
    esper.create_entity(
        Position(UI_MARGIN, 92), Renderable(image=image), Layer(5), Dirty(1), OwnedBy("map.world"))


class _ClockFooterProcessor(esper.Processor):
    """Ports the old Map.update() override: keeps LOCAL's footer date/time
    live while it's on screen. Priority 32 so it runs before UIRenderProcessor
    (30) in the same frame -- otherwise a section change wouldn't be picked up
    until the following frame."""

    def __init__(self, footer_ent):
        self.footer_ent = footer_ent

    def process(self, dt):
        if not esper.has_component(self.footer_ent, Active):
            return
        state = esper.component_for_entity(self.footer_ent, FooterState)
        now = datetime.now()
        changed_date = state.update_section(0, now.strftime("%d.%m.%Y"))
        changed_time = state.update_section(1, now.strftime("%H:%M:%S"))
        if changed_date or changed_time:
            esper.component_for_entity(self.footer_ent, Dirty).state = 1
