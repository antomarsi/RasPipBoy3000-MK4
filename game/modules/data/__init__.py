from core.components import Dirty, Layer, Position, Renderable
from game.data.store import save_data
from game.modules.registry import create_node
from game.ui import UI_MARGIN, MenuState


def register(pipboy):
    create_node("data", "DATA")
    _register_quests()
    _register_workshops()
    _register_stats()


def _register_quests():
    titles = [f"{q.get('title', '?')} ({q.get('status', '?')})" for q in save_data.quests]
    create_node("data.quests", "QUESTS", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=titles),
    ])


def _register_workshops():
    titles = [f"{w.get('name', '?')} (pop {w.get('population', '?')})" for w in save_data.workshops]
    create_node("data.workshops", "WORKSHOPS", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=titles),
    ])


def _register_stats():
    # No dedicated gameplay-stats model exists yet (see the plan's
    # "Explicitly out of scope" section) -- shows what's already real (player
    # progression) rather than inventing placeholder counters.
    player = save_data.player
    items = [
        f"LEVEL: {player.level}",
        f"TOTAL XP: {player.total_exp}",
        f"NEXT LEVEL XP: {player.next_level_xp}",
    ]
    create_node("data.stats", "STATS", parent="data", components=[
        Position(UI_MARGIN, 92), Renderable(), Layer(5), Dirty(1), MenuState(items=items),
    ])
