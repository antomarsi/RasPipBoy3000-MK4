import textwrap

import esper

from core.components import Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data.catalog import special as special_catalog
from game.data.store import theme
from game.modules.registry import create_node
from game.ui import UI_MARGIN, render_text

NODE_KEY = "stat.special"


def register(pipboy):
    create_node(NODE_KEY, "SPECIAL", parent="stat")
    _register_content()


def _register_content():
    # catalog.special's per-stat `images` (assets/data/special.json) don't
    # actually exist on disk yet -- only the description text is real content
    # today. Animating the stat icons is tracked as catalog/asset follow-up
    # work (see the plan's "Explicitly out of scope" section), not wired here
    # to avoid crashing on missing files.
    name, info = next(iter(special_catalog.items()))
    color = theme.draw_color

    title_font = ResourceLoader.get_font("MONOFONTO", 30)
    title_image = render_text(title_font, name.upper(), color)
    esper.create_entity(
        Position(UI_MARGIN, 100), Renderable(image=title_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))

    body_font = ResourceLoader.get_font("ROBOTO", 24)
    wrapped = textwrap.wrap(info["description"], width=48)
    line_height = body_font.get_height() + 4
    for index, line in enumerate(wrapped):
        line_image = render_text(body_font, line, color)
        esper.create_entity(
            Position(UI_MARGIN, 150 + index * line_height), Renderable(image=line_image),
            Layer(5), Dirty(1), OwnedBy(NODE_KEY))
