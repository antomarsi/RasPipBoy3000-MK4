import esper

from core.components import Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data.store import save_data, theme
from game.modules.registry import create_node
from game.ui import UI_MARGIN, MenuState, menu_right_column_left, render_text

_RIGHT_COLUMN_LEFT = menu_right_column_left()
_RIGHT_COLUMN_TOP = 92
_ROW_HEIGHT = 33


def register(pipboy):
    create_node("data", "DATA")
    _register_quests()
    _register_stats()


def _register_quests():
    color = theme.draw_color
    quests = save_data.quests
    titles = [f"{q.get('title', '?')} ({q.get('status', '?')})" for q in quests]

    obj_font = ResourceLoader.get_font("MONOFONTO", 24)
    max_objectives = max((len(q.get("objectives", [])) for q in quests), default=0)
    obj_ents = [
        esper.create_entity(
            Position(_RIGHT_COLUMN_LEFT, 0), Renderable(visible=False), Layer(5), Dirty(1), OwnedBy("data.quests"))
        for _ in range(max_objectives)
    ]

    def refresh(index):
        objectives = quests[index].get("objectives", []) if index < len(quests) else []
        for row_index, ent in enumerate(obj_ents):
            renderable = esper.component_for_entity(ent, Renderable)
            if row_index < len(objectives):
                renderable.image = render_text(obj_font, f"- {objectives[row_index]}", color)
                renderable.visible = True
                esper.component_for_entity(ent, Position).y = _RIGHT_COLUMN_TOP + row_index * _ROW_HEIGHT
            else:
                renderable.visible = False
            esper.component_for_entity(ent, Dirty).state = 1

    menu_state = MenuState(items=titles, on_change=refresh)
    create_node("data.quests", "QUESTS", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), menu_state,
    ])

    refresh(0)


def _register_stats():
    # No dedicated gameplay-stats model exists yet (see the follow-up
    # content plan) -- shows what's already real (player progression)
    # rather than inventing placeholder counters.
    player = save_data.player
    items = [
        f"LEVEL: {player.level}",
        f"TOTAL XP: {player.total_exp}",
        f"NEXT LEVEL XP: {player.next_level_xp}",
    ]
    create_node("data.stats", "STATS", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=items),
    ])
