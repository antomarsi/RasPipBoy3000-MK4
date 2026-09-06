import esper

from core.components import Dirty, Layer, OwnedBy, Position, Renderable
from game.modules.registry import create_node
from game.modules.stat import perks, special, status
from game.ui import UI_MARGIN, FooterState, ProgressBarState, render_progressbar
from utils.settings import config


def register(pipboy):
    create_node("stat", "STAT")
    _register_footer()
    status.register(pipboy)
    special.register(pipboy)
    perks.register(pipboy)


def _register_footer():
    # Owned by "stat" (the top-level node), not any one leaf -- shared across
    # STATUS/SPECIAL/PERKS, matching the real Pip-Boy (every STAT sub-screen
    # keeps HP/LEVEL/AP visible).
    progressbar_image = render_progressbar(ProgressBarState(
        dimensions=(200, 29), value=26, max_value=100, border_width=2, margin=(0, 4, 0, 4)))
    footer_state = FooterState(sections=["HP 90/100", [["LEVEL 120", progressbar_image], 2], "AP 90/90"])
    esper.create_entity(
        Position(UI_MARGIN, config.HEIGHT - 45), Renderable(), Layer(5), Dirty(1),
        footer_state, OwnedBy("stat"))
