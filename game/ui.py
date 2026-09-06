"""Pure-data UI widgets for the ECS render pipeline.

Each *State dataclass below is a widget's state; UIRenderProcessor turns a
state change into a rebuilt Renderable.image whenever the owning entity's
Dirty is armed. Mutating a *State in place does NOT redraw by itself -- the
mutator must also arm Dirty (e.g. `esper.add_component(footer_ent, Dirty(1))`),
same convention used by the rest of the ECS (see core/processors.py).

Supersedes the old sprite-based Header/SubMenu/Footer/Menu/ProgressBar classes
(deleted in Phase 5 along with core.engine.Entity/EntityGroup and
game.modules.BaseModule/SubModule -- see the architecture plan).
"""
from dataclasses import dataclass, field
from typing import Optional

import esper
import pygame as pg

from core.components import Dirty, Renderable
from core.resource_loader import ResourceLoader
from game.data.store import theme
from utils.layout import layout_flex_row
from utils.settings import config

UI_MARGIN = 14


@dataclass
class HeaderState:
    label: Optional[str] = None
    options: list = field(default_factory=list)
    color: tuple = theme.draw_color
    bg_color: tuple = theme.bg_color


@dataclass
class SubMenuState:
    options: list = field(default_factory=list)
    active_index: int = 0
    color: tuple = theme.draw_color
    bg_color: tuple = theme.bg_color


@dataclass
class FooterState:
    sections: list = field(default_factory=list)
    color: tuple = theme.draw_color
    bg_color: tuple = theme.bg_color
    padding: int = 4

    def update_section(self, index: int, value) -> bool:
        if index >= len(self.sections):
            raise Exception("Index not found")
        if self.sections[index] != value:
            self.sections[index] = value
            return True
        return False


@dataclass
class MenuState:
    items: list = field(default_factory=list)
    selected: int = 0
    index: int = 0
    max_items: int = 7
    color: tuple = theme.draw_color
    bg_color: tuple = theme.bg_color


@dataclass
class ProgressBarState:
    dimensions: tuple = (0, 0)
    value: float = 0
    max_value: float = 1
    color: tuple = theme.draw_color
    bg_color: tuple = (0, 0, 0, 0)
    border_width: int = 1
    margin: tuple = (0, 0, 0, 0)


def render_text(font, text: str, color, bg_color=theme.bg_color) -> pg.Surface:
    """A standalone label, pre-flattened onto an opaque background.

    RenderProcessor composites everything with additive blending (to match
    the app's CRT-glow look -- see core/processors.py), which does NOT weigh
    by source alpha. A bare `font.render(...)` result has a transparent
    background with partially-transparent anti-aliased edges, and additive
    blending an unweighted anti-aliased image paints every touched pixel at
    full brightness -- text reads as a solid blob instead of glyphs. Baking
    the text onto an opaque surface first (like every other widget in this
    module already does) resolves the anti-aliasing before the additive
    compositing step, avoiding that."""
    text_surface = font.render(text, True, color)
    image = pg.Surface(text_surface.get_size())
    image.fill(bg_color)
    image.blit(text_surface, (0, 0))
    return image


def render_header(state: HeaderState) -> pg.Surface:
    width, height = config.WIDTH - (UI_MARGIN * 2), 60
    image = pg.Surface((width, height))
    image.fill(state.bg_color)
    font = ResourceLoader.get_font("MONOFONTO", 30)

    LINE_WIDTH = 3
    short_line_margin = 10
    lines_selection = [(2, height), (2, height - short_line_margin)]
    next_position = 80
    selected_position = 0
    selected_text = None

    options = [str(x) for x in state.options]
    tab_area_width = config.WIDTH * 0.8
    tab_spacing = tab_area_width / (len(options) - 1)

    text_surfaces = []
    current_index = None
    for idx, text in enumerate(options):
        if text == state.label:
            current_index = idx
        text_surf = font.render(text, True, state.color)
        tab_area_width -= text_surf.get_width()
        text_surfaces.append(text_surf)
    if current_index is None and text_surfaces:
        # state.label doesn't match any option (e.g. a transient initial
        # state before the first real chrome update) -- fall back to the
        # first tab instead of leaving selected_text as None below.
        current_index = 0
    tab_spacing = tab_spacing / (len(options) - 1)

    for index, text_surface in enumerate(text_surfaces):
        if index == current_index:
            selected_position = next_position
            selected_text = text_surface
            next_position += tab_spacing + text_surface.get_width()
            continue
        image.blit(text_surface, (next_position, 14))
        next_position += tab_spacing + text_surface.get_width()

    selected_margin = 28
    selected_line_margin = 14
    lines_selection.append((selected_position - selected_line_margin - 1, height - short_line_margin))
    lines_selection.append((selected_position - selected_line_margin - 1, selected_margin))
    lines_selection.append((selected_position + selected_line_margin - 1 + selected_text.get_width(), selected_margin))
    lines_selection.append((selected_position + selected_line_margin - 1 + selected_text.get_width(), height - short_line_margin))
    lines_selection.append((width - 2, height - short_line_margin))
    lines_selection.append((width - 2, height))

    pg.draw.lines(image, state.color, False, lines_selection, LINE_WIDTH)
    pg.draw.rect(image, state.bg_color, (selected_position - 6, 26, selected_text.get_width() + 12, 12))
    image.blit(selected_text, (selected_position, 14))
    return image


def render_submenu(state: SubMenuState) -> pg.Surface:
    width, height = config.WIDTH - 80, 32
    image = pg.Surface((width, height))
    image.fill(state.bg_color)
    font = ResourceLoader.get_font("MONOFONTO", 30)

    options = [str(x) for x in state.options]
    margin = 0
    for idx, text in enumerate(options):
        division = abs(idx - state.active_index) + 1
        if division > 2:
            division += 2
        if division <= 5:
            color = (state.color[0] / division, state.color[1] / division, state.color[2] / division)
        else:
            color = state.bg_color
        text_surf = font.render(text, True, color).convert_alpha()
        image.blit(text_surf, (margin, 0))
        margin += text_surf.get_width() + 18
    return image


def _parse_footer_sections(sections):
    parsed = []
    for value in sections:
        section, size = value, 1
        if isinstance(value, (tuple, list)):
            section = value[0]
            if len(value) > 1:
                size = value[1]
        parsed.append((section, size))
    return parsed


def _render_footer_section(font, color, value, available_width: int):
    if isinstance(value, str):
        return font.render(value, True, color)
    if isinstance(value, pg.Surface):
        return value
    if isinstance(value, list):
        rendered = [font.render(v, True, color) if isinstance(v, str) else v for v in value]
        height = max((s.get_height() for s in rendered), default=0)
        return layout_flex_row(rendered, pg.Rect(0, 0, available_width, height), 8)
    raise Exception("Failed to parse footer section")


def render_footer(state: FooterState) -> pg.Surface:
    width, height = config.WIDTH - (UI_MARGIN * 2), 30
    image = pg.Surface((width, height))
    image.fill(state.bg_color)
    font = ResourceLoader.get_font("MONOFONTO", 24)

    if not state.sections:
        return image

    sections = _parse_footer_sections(state.sections)
    total_size = sum(size for (_, size) in sections)
    rect_size = (width - (state.padding * (total_size - 1))) / total_size
    box_color = (state.color[0] / 2, state.color[1] / 2, state.color[2] / 2)

    next_pos = 0
    for section, size in sections:
        current_size = (rect_size * size) + (state.padding * (size - 1))
        rect = pg.Rect(next_pos, 0, current_size, height)
        pg.draw.rect(image, box_color, rect)

        surface = _render_footer_section(font, state.color, section, int(current_size))
        if surface is not None:
            image.blit(surface, (next_pos + state.padding, 0))

        next_pos += current_size + state.padding

    return image


def _render_menu_item(font, soft_color, bg_color, menu_width, item_height, text, selected):
    surface = pg.Surface((menu_width * 0.55, item_height))
    text_color = soft_color
    if selected:
        text_color = bg_color
        surface.fill(soft_color)
    font_surf = font.render(text, True, text_color)
    surface.blit(font_surf, (20, surface.get_rect().centery - font_surf.get_height() / 2))
    return surface


def render_menu(state: MenuState) -> pg.Surface:
    width, height = config.WIDTH - UI_MARGIN * 2, config.HEIGHT - 172
    image = pg.Surface((width, height))
    font = ResourceLoader.get_font("MONOFONTO", 24)
    soft_color = (state.color[0] * 0.65, state.color[1] * 0.65, state.color[2] * 0.65)
    menu_item_size = 38

    pg.draw.rect(image, state.color, (0, 0, width * 0.45, menu_item_size))

    item_count = 0
    for idx, item in enumerate(state.items):
        if idx < state.index or item_count >= state.max_items:
            continue
        item_count += 1
        position_y = (idx - state.index) * menu_item_size
        surf = _render_menu_item(font, soft_color, state.bg_color, width, menu_item_size, item, idx == state.selected)
        image.blit(surf, (0, position_y))
    return image


def menu_handle_action(state: MenuState, action: str) -> bool:
    """dial_up/dial_down for a MenuState -- ports game/ui.py's Menu.select()
    scrolling behavior. Returns True if `selected`/`index` changed, so the
    caller knows whether to arm Dirty(1) on the owning entity."""
    if action == "dial_up":
        target = state.selected - 1
    elif action == "dial_down":
        target = state.selected + 1
    else:
        return False

    if not state.items:
        return False

    target = min(max(target, 0), len(state.items) - 1)
    if target == state.selected:
        return False

    if target > state.index + state.max_items - 1:
        state.index = target - state.max_items + 1
    if state.index > target:
        state.index = target

    state.selected = target
    return True


def render_progressbar(state: ProgressBarState) -> pg.Surface:
    image = pg.Surface(state.dimensions, flags=pg.SRCALPHA)
    image.fill(state.bg_color)

    fill_value = state.value / state.max_value if state.max_value else 0
    draw_rect = image.get_rect()
    draw_rect.top += state.margin[1]
    draw_rect.left += state.margin[0]
    draw_rect.width -= state.margin[2] + state.margin[0]
    draw_rect.height -= state.margin[3] + state.margin[1]

    pg.draw.rect(image, state.color, pg.Rect(
        draw_rect.left, draw_rect.top, draw_rect.width * fill_value, draw_rect.height))
    pg.draw.rect(image, state.color, draw_rect, state.border_width)
    return image


_RENDERERS = {
    HeaderState: render_header,
    SubMenuState: render_submenu,
    FooterState: render_footer,
    MenuState: render_menu,
    ProgressBarState: render_progressbar,
}


class UIRenderProcessor(esper.Processor):
    """Rebuilds Renderable.image from a *State component whenever the entity's
    Dirty is armed (state >= 1, or no Dirty component at all).

    Mirrors AnimationProcessor's convention: this only ARMS a fresh image, it
    does not reset Dirty.state itself. core/processors.py's RenderProcessor is
    the sole place that resets state 1 -> 0, once it has accounted for the
    change in dirty_this_frame (the battery idle-framerate signal) -- clearing
    it here would hide the change from RenderProcessor within the same frame.
    """

    def process(self, dt=None):
        for state_type, renderer in _RENDERERS.items():
            for ent, (state, renderable) in esper.get_components(state_type, Renderable):
                dirty = esper.try_component(ent, Dirty)
                if dirty and dirty.state < 1:
                    continue
                renderable.image = renderer(state)
