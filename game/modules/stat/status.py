import pygame as pg
import esper

from core.components import AnimationState, Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data import catalog
from game.data.store import player_status, save_data, theme
from game.modules.registry import create_node
from game.ui import UI_MARGIN, ProgressBarState, fit_icon, render_progressbar
from utils.settings import config

NODE_KEY = "stat.status"

_BOTTOM_TEXT_Y = config.HEIGHT - 79

_RESISTANCE_ICON_BOX = (28, 28)
_RESISTANCE_GAP_ABOVE_BOTTOM_TEXT = 16
_RESISTANCE_ROW_Y = _BOTTOM_TEXT_Y - _RESISTANCE_GAP_ABOVE_BOTTOM_TEXT - _RESISTANCE_ICON_BOX[1]

_EFFECTS_ICON_BOX = (24, 24)
_EFFECTS_GAP_ABOVE_RESISTANCE = 12
_EFFECTS_ROW_Y = _RESISTANCE_ROW_Y - _EFFECTS_GAP_ABOVE_RESISTANCE - _EFFECTS_ICON_BOX[1]


def register(pipboy):
    create_node(NODE_KEY, "STATUS", parent="stat")
    _register_vaultboy_anim()
    _register_bottom_text()
    _register_health_bars()
    _register_resistance_row()
    _register_status_effects()


def _build_vaultboy_frames(color):
    body_frames = [
        ResourceLoader.add_image(f"body_ok_0_{x}", f"images/health_cond/icon_condition_body_0_{x}.png")
        for x in range(8)
    ]
    head = ResourceLoader.add_image("head_ok_0", "images/health_cond/head_normal.png")
    body_w, body_h = body_frames[0].get_size()
    total_h = body_h + head.get_height()

    frames = []
    for body in body_frames:
        surface = pg.Surface((body_w, total_h))
        surface.blit(head, (27, 10))
        surface.blit(body, (0, total_h - body_h))
        surface.fill(color, special_flags=pg.BLEND_MULT)
        frames.append(surface)
    return frames


def _register_vaultboy_anim():
    frames = _build_vaultboy_frames(theme.draw_color)
    body_w, total_h = frames[0].get_size()
    x = config.WIDTH * 0.5 - body_w / 2
    y = config.HEIGHT * 0.45 - total_h / 2
    esper.create_entity(
        Position(x, y), Renderable(image=frames[0]), Layer(5), Dirty(2),
        AnimationState(frames=frames, duration_per_frame=0.1, loop=True, playing=True),
        OwnedBy(NODE_KEY))


def _render_bottom_text(font, text, quantity, color):
    bg_color = tuple(c * 0.75 for c in color)
    text_color = tuple(c * 0.5 for c in color)
    text_surface = font.render(f"{text.upper()}({quantity})", True, text_color)
    image = pg.Surface((text_surface.get_width() + 7, text_surface.get_height()))
    image.fill(bg_color)
    image.blit(text_surface, (4, -1))
    return image


def _register_bottom_text():
    font = ResourceLoader.get_font("MONOFONTO", 24)
    color = theme.draw_color

    stimpak_image = _render_bottom_text(font, "Stimpak", 0, color)
    stim_x, stim_y = 50, _BOTTOM_TEXT_Y
    esper.create_entity(Position(stim_x, stim_y), Renderable(image=stimpak_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))

    radaway_image = _render_bottom_text(font, "Radaway", 0, color)
    radaway_x = stim_x + stimpak_image.get_width() + 14
    esper.create_entity(Position(radaway_x, stim_y), Renderable(image=radaway_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))


def _register_health_bars():
    left, top = config.WIDTH * 0.1, 92
    width, height = config.WIDTH * 0.8, config.HEIGHT - 172
    bar_size = (32, 9)
    half_width = width / 2

    # (body_parts key, local centerx, local top) within the old
    # HealthContainer's rect, translated to absolute screen positions below.
    # Real per-limb condition, driven by PlayerStatus.body_parts (was always
    # hardcoded to 100% before, even though this field already existed).
    positions = [
        ("head", half_width + 4, height * 0.06),
        ("left_arm", half_width * 0.63, height * 0.3),
        ("left_leg", half_width * 0.63, height * 0.61),
        ("right_arm", half_width * 1.38, height * 0.3 + 1),
        ("right_leg", half_width * 1.38, height * 0.61 + 1),
    ]

    for part, local_centerx, local_top in positions:
        condition = max(0.0, min(1.0, player_status.body_parts.get(part, 1.0))) * 100
        image = render_progressbar(ProgressBarState(dimensions=bar_size, value=condition, max_value=100, border_width=1))
        x = left + local_centerx - bar_size[0] / 2
        y = top + local_top
        esper.create_entity(Position(x, y), Renderable(image=image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))

    # "Full" bar -- overall condition, derived from current/max HP (the same
    # figure the shared footer already shows) rather than averaging limbs.
    full_pct = (player_status.current_hp / player_status.max_hp * 100) if player_status.max_hp else 0
    full_image = render_progressbar(ProgressBarState(dimensions=bar_size, value=full_pct, max_value=100, border_width=1))
    full_x = left + (half_width + 4) - bar_size[0] / 2
    full_y = top + height * 0.72 + 14
    esper.create_entity(Position(full_x, full_y), Renderable(image=full_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))


def _equipped_weapon_damage() -> int:
    equipped = next((item for item in save_data.inventory.get("weapons", []) if item.eqp), None)
    if not equipped:
        return 0
    info = catalog.weapons.get(equipped.baseid)
    return info.get("damage", 0) if info else 0


def _total_apparel_stat(field: str) -> float:
    total = 0.0
    for item in save_data.inventory.get("apparel", []):
        if not item.eqp:
            continue
        info = catalog.apparel.get(item.baseid)
        if info:
            total += info.get(field, 0)
    return total


def _build_icon_value_row(entries, icon_box, row_width):
    """entries: list of (icon_name, value_text). Renders icon+value pairs
    left to right onto an opaque row (safe as a Renderable.image -- see
    game.ui.fit_icon's docstring on why additive blending needs that)."""
    color = theme.draw_color
    font = ResourceLoader.get_font("MONOFONTO", 24)
    row_height = icon_box[1]

    row_image = pg.Surface((row_width, row_height))
    row_image.fill(theme.bg_color)

    x = 0
    for icon_name, value_text in entries:
        icon = fit_icon(ResourceLoader.add_image(f"stat_icon_{icon_name}", f"img/stats/{icon_name}.png"), color, icon_box)
        text_surf = font.render(value_text, True, color)
        row_image.blit(icon, (x, (row_height - icon.get_height()) // 2))
        x += icon.get_width() + 6
        row_image.blit(text_surf, (x, (row_height - text_surf.get_height()) // 2))
        x += text_surf.get_width() + 28

    return row_image


def _register_resistance_row():
    # Matches the real Pip-Boy's STATUS screen: equipped weapon's damage,
    # then DR/ER/RR summed across every equipped apparel item (there's no
    # separate armor-slot concept in this schema, just an `eqp` flag per
    # item, so "equipped" apparel can be more than one piece at once).
    entries = [
        ("gun", str(_equipped_weapon_damage())),
        ("armor", str(int(_total_apparel_stat("DR")))),
        ("thunder", str(int(_total_apparel_stat("ER")))),
        ("radioactive", str(int(_total_apparel_stat("RR")))),
    ]
    row_image = _build_icon_value_row(entries, _RESISTANCE_ICON_BOX, config.WIDTH - UI_MARGIN * 2)
    esper.create_entity(
        Position(UI_MARGIN, _RESISTANCE_ROW_Y), Renderable(image=row_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))


def _register_status_effects():
    # Driven entirely by PlayerStatus fields that already exist but were
    # never displayed anywhere (`radiaton`, `drugs`). No new schema needed
    # for this minimal-but-real version; broader effects (addictions,
    # Survival-mode needs) stay follow-up work.
    entries = []
    if player_status.radiaton > 0:
        entries.append(("radioactive", f"RADIATION {player_status.radiaton}"))
    if player_status.drugs:
        entries.append(("poison", "DRUGGED"))

    if not entries:
        return

    row_image = _build_icon_value_row(entries, _EFFECTS_ICON_BOX, config.WIDTH - UI_MARGIN * 2)
    esper.create_entity(
        Position(UI_MARGIN, _EFFECTS_ROW_Y), Renderable(image=row_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))
