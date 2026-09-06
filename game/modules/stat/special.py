import textwrap

import esper
import pygame as pg

from core.components import AnimationState, Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data.catalog import special as special_catalog
from game.data.store import player_status, theme
from game.modules.registry import create_node
from game.ui import UI_MARGIN, MenuState, render_text
from utils.layout import scale_surface_keep_aspect
from utils.settings import config

NODE_KEY = "stat.special"

# game/data/player.py's PlayerStatus keeps the original (misspelled)
# field names -- map SPECIAL display names to them here rather than
# propagating the typos into this module.
PLAYER_FIELD = {
    "Strength": "strenght",
    "Perception": "perception",
    "Endurance": "endurance",
    "Charisma": "charisma",
    "Intelligence": "inteligence",
    "Agility": "agility",
    "Luck": "luck",
}

# MenuState (the left list) always renders at a hardcoded full width
# (config.WIDTH - UI_MARGIN*2, see game/ui.py's render_menu) with each row's
# own content occupying the left 55% of that -- i.e. real list content
# extends all the way out to UI_MARGIN + (WIDTH - UI_MARGIN*2)*0.55, not just
# the visually-obvious label column. The right column below has to start
# past that or a row's right-aligned value can land underneath (additive
# blending doesn't hide it -- two overlapping glyphs just add together).
_LIST_CONTENT_RIGHT = UI_MARGIN + (config.WIDTH - UI_MARGIN * 2) * 0.55
_RIGHT_COLUMN_LEFT = _LIST_CONTENT_RIGHT + 16
_RIGHT_COLUMN_RIGHT = config.WIDTH - UI_MARGIN
_ICON_TOP = 90
# Source icon frames come from a sprite rip with wildly inconsistent canvas
# sizes per frame -- from 118px to 556px tall, nominally all 160px wide, with
# no consistent relationship between canvas size and the actual character's
# size within it (trimming artifacts, not intentional variation). Fitting
# each frame into this fixed box and centering it there, rather than just
# scaling to a fixed height, is what keeps the layout below it predictable
# and stops an unusually wide fitted frame from overlapping the list or the
# description text.
_ICON_BOX = (200, 220)
_GAP = 16
_MAX_DESC_LINES = 6
_DESC_WRAP_WIDTH = 28
_BOTTOM_MARGIN = 12


def _fit_frame(source: pg.Surface, color) -> pg.Surface:
    # Icons are white line art on a transparent background -- composite onto
    # opaque black first, then BLEND_MULT-tint white -> theme color (same
    # technique as stat/status.py's vault-boy animation), since
    # RenderProcessor's additive-blend compositing needs an opaque, already
    # colored frame, not a raw alpha image.
    tinted = pg.Surface(source.get_size())
    tinted.blit(source, (0, 0))
    tinted.fill(color, special_flags=pg.BLEND_MULT)

    fitted = scale_surface_keep_aspect(tinted, max_width=_ICON_BOX[0], max_height=_ICON_BOX[1])
    canvas = pg.Surface(_ICON_BOX)
    canvas.blit(fitted, ((_ICON_BOX[0] - fitted.get_width()) / 2, (_ICON_BOX[1] - fitted.get_height()) / 2))
    return canvas


def register(pipboy):
    color = theme.draw_color
    names = list(special_catalog.keys())
    items = [(name.upper(), getattr(player_status, PLAYER_FIELD[name])) for name in names]

    icon_x = (_RIGHT_COLUMN_LEFT + _RIGHT_COLUMN_RIGHT) / 2 - _ICON_BOX[0] / 2
    anim_ent = esper.create_entity(
        Position(icon_x, _ICON_TOP), Renderable(), Layer(5), Dirty(1),
        AnimationState(duration_per_frame=0.15, loop=True), OwnedBy(NODE_KEY))

    desc_font = ResourceLoader.get_font("ROBOTO", 24)
    desc_ents = [
        esper.create_entity(
            Position(_RIGHT_COLUMN_LEFT, 0), Renderable(visible=False), Layer(5), Dirty(1), OwnedBy(NODE_KEY))
        for _ in range(_MAX_DESC_LINES)
    ]

    frame_cache: dict[str, list] = {}

    def _frames_for(name, info):
        if name not in frame_cache:
            frame_cache[name] = [
                _fit_frame(ResourceLoader.add_image(f"special_{name}_{i}", path), color)
                for i, path in enumerate(info["images"])
            ]
        return frame_cache[name]

    def refresh(index):
        name = names[index]
        info = special_catalog[name]
        frames = _frames_for(name, info)

        anim = esper.component_for_entity(anim_ent, AnimationState)
        anim.frames = frames
        anim.current_frame = 0
        anim.elapsed = 0.0
        anim.playing = True
        anim.finished = False
        esper.component_for_entity(anim_ent, Renderable).image = frames[0]
        esper.component_for_entity(anim_ent, Dirty).state = 2

        desc_top = _ICON_TOP + _ICON_BOX[1] + _GAP
        line_height = desc_font.get_height() + 4
        lines_that_fit = max(1, (config.HEIGHT - _BOTTOM_MARGIN - desc_top) // line_height)
        wrapped = textwrap.wrap(info["description"], width=_DESC_WRAP_WIDTH)[:min(_MAX_DESC_LINES, lines_that_fit)]
        for line_index, ent in enumerate(desc_ents):
            renderable = esper.component_for_entity(ent, Renderable)
            if line_index < len(wrapped):
                renderable.image = render_text(desc_font, wrapped[line_index], color)
                renderable.visible = True
                esper.component_for_entity(ent, Position).y = desc_top + line_index * line_height
            else:
                renderable.visible = False
            esper.component_for_entity(ent, Dirty).state = 1

    menu_state = MenuState(items=items, on_change=refresh)
    create_node(NODE_KEY, "SPECIAL", parent="stat", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), menu_state,
    ])

    refresh(0)
