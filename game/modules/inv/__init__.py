import esper
import pygame as pg

from core.components import Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data import catalog
from game.data.store import INVENTORY_CATEGORIES, save_data, theme
from game.modules.registry import create_node
from game.ui import UI_MARGIN, FooterState, MenuState, fit_icon
from utils.settings import config

# category -> its catalog dict (baseid -> item).
CATALOGS = {
    "weapons": catalog.weapons,
    "apparel": catalog.apparel,
    "aid": catalog.aid,
    "misc": catalog.misc,
    "junk": catalog.junk,
    "mods": catalog.mods,
    "ammo": catalog.ammo,
}

# Same list-widget geometry SPECIAL uses: MenuState always renders at a
# hardcoded full width with each row's own content occupying the left 55% of
# that (see game/ui.py's render_menu) -- the right column has to start past
# that real content width, not a guessed constant.
_RIGHT_COLUMN_LEFT = UI_MARGIN + (config.WIDTH - UI_MARGIN * 2) * 0.55 + 16
_RIGHT_COLUMN_TOP = 92
_ROW_HEIGHT = 33
_STAT_ICON_BOX = (28, 28)
_FOOTER_ICON_BOX = (20, 20)

_icon_cache: dict[str, pg.Surface] = {}


def _stat_icon(name: str, box: tuple) -> pg.Surface:
    """assets/img/stats/<name>.png, tinted + fit into `box`, cached. `name`
    can come straight from a catalog field (e.g. a weapon's own
    "damage_icon") -- see _resolve_icon() -- so a new icon is just a new PNG
    plus a JSON edit, not a code change."""
    key = f"{name}:{box}"
    if key not in _icon_cache:
        raw = ResourceLoader.add_image(f"stat_icon_{name}", f"img/stats/{name}.png")
        _icon_cache[key] = fit_icon(raw, theme.draw_color, box)
    return _icon_cache[key]


def _resolve_icon(field_def: dict, info: dict):
    """An icon spec is either a fixed name (same icon every time, e.g.
    "weight") or {"from_field": "..."} to look the name up on the item
    itself -- modular per-item icons (a weapon's damage icon depends on its
    own damage_icon field: "aim" for normal damage, "thunder" for energy,
    etc.) without any per-category special-casing here."""
    icon_spec = field_def.get("icon")
    if icon_spec is None:
        return None
    if isinstance(icon_spec, dict):
        return info.get(icon_spec["from_field"])
    return icon_spec


def _render_stat_row(font, label, value, color, bg_color, icon: pg.Surface = None) -> pg.Surface:
    value_text = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)
    row_width = int(config.WIDTH - UI_MARGIN - _RIGHT_COLUMN_LEFT)
    label_surf = font.render(label, True, color)
    value_surf = font.render(value_text, True, color)
    height = max(label_surf.get_height(), value_surf.get_height(), icon.get_height() if icon else 0)

    image = pg.Surface((row_width, height))
    image.fill(bg_color)
    x = 0
    if icon is not None:
        image.blit(icon, (0, (height - icon.get_height()) / 2))
        x = icon.get_width() + 8
    image.blit(label_surf, (x, (height - label_surf.get_height()) / 2))
    image.blit(value_surf, (row_width - value_surf.get_width(), (height - value_surf.get_height()) / 2))
    return image


def _total_weight() -> float:
    total = 0.0
    for category, catalog_map in CATALOGS.items():
        for item in save_data.inventory.get(category, []):
            info = catalog_map.get(item.baseid)
            if info:
                total += info.get("weight", 0) * item.qtd
    return total


def register(pipboy):
    create_node("inv", "INV")
    _register_footer()
    for category in INVENTORY_CATEGORIES:
        _register_category(category)


def _register_footer():
    equipped = next((item for item in save_data.inventory.get("weapons", []) if item.eqp), None)
    equipped_info = catalog.weapons.get(equipped.baseid) if equipped else None
    if equipped_info:
        damage = equipped_info.get("damage")
        equipped_label = equipped_info["title"] + (f"  {damage}" if damage is not None else "")
    else:
        equipped_label = "NONE EQUIPPED"

    footer_state = FooterState(sections=[
        [[_stat_icon("weight", _FOOTER_ICON_BOX), f"{_total_weight():.1f}/{save_data.max_weight:.0f}"], 1],
        [[_stat_icon("caps", _FOOTER_ICON_BOX), f"{save_data.caps}"], 1],
        [[_stat_icon("gun", _FOOTER_ICON_BOX), equipped_label], 2],
    ])
    esper.create_entity(
        Position(UI_MARGIN, config.HEIGHT - 45), Renderable(), Layer(5), Dirty(1),
        footer_state, OwnedBy("inv"))


def _register_category(category):
    node_key = f"inv.{category}"
    owned_items = save_data.inventory.get(category, [])
    catalog_map = CATALOGS[category]
    resolved = [(item, catalog_map[item.baseid]) for item in owned_items if item.baseid in catalog_map]
    titles = [info["title"] for _, info in resolved]

    stat_font = ResourceLoader.get_font("MONOFONTO", 24)
    stat_fields = catalog.categories.get(category, {}).get("stats", [])
    stat_ents = [
        esper.create_entity(
            Position(_RIGHT_COLUMN_LEFT, 0), Renderable(visible=False), Layer(5), Dirty(1), OwnedBy(node_key))
        for _ in stat_fields
    ]

    def refresh(index):
        info = resolved[index][1] if index < len(resolved) else None
        for row_index, (field_def, ent) in enumerate(zip(stat_fields, stat_ents)):
            renderable = esper.component_for_entity(ent, Renderable)
            value = info.get(field_def["field"]) if info else None
            if value is None:
                renderable.visible = False
            else:
                icon_name = _resolve_icon(field_def, info)
                icon = _stat_icon(icon_name, _STAT_ICON_BOX) if icon_name else None
                renderable.image = _render_stat_row(
                    stat_font, field_def["label"], value, theme.draw_color, theme.bg_color, icon)
                renderable.visible = True
                esper.component_for_entity(ent, Position).y = _RIGHT_COLUMN_TOP + row_index * _ROW_HEIGHT
            esper.component_for_entity(ent, Dirty).state = 1

    menu_state = MenuState(items=titles, on_change=refresh)
    create_node(node_key, category.upper(), parent="inv", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), menu_state,
    ])

    refresh(0)
