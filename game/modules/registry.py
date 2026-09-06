"""The module tree: registration, activation, and action dispatch.

Replaces the old two-level BaseModule/SubModule split with a single recursive
concept -- a Node is a top-level tab, a submodule, or (not exercised by any
real content yet, but supported) a level below that. Depth is just how many
`parent` links you follow.

A node's own esper entity carries a `Node` component and, optionally, visual
components directly (e.g. a leaf with exactly one widget, like an INV
category's MenuState). A node that needs several visual pieces (STAT.status's
footer + vault-boy animation + health bars) instead owns several separate
entities tagged `OwnedBy(node.key)`. switch_node() activates/deactivates a
node and everything it owns as one group.

Background nodes (NodeDescriptor.background = True, e.g. RADIO) keep the
`Running` tag when they lose `Active` on tab-away, so a future processor that
queries `Running` (e.g. an audio tick) keeps executing while a different tab
is on screen.
"""
from typing import Optional

import esper

from core.components import Active, Dirty, Layer, Node, OwnedBy, Position, Renderable, Running
from game.ui import UI_MARGIN, HeaderState, MenuState, SubMenuState, menu_handle_action
from utils.logger import logger

# key -> entity id, for every registered node.
NODES: dict[str, int] = {}
# key -> display label ("stat.status" -> "STATUS").
LABELS: dict[str, str] = {}

# Top-level tabs shown in the header, in display order. `boot` is
# intentionally excluded -- it isn't a user-navigable tab, just the startup
# sequence (PipBoy.init_modules() enters it directly unless SKIP_INTRO).
TOP_LEVEL = ["stat", "inv", "data", "map", "radio"]

ACTIVE_LEAF: Optional[str] = None

_header_ent: Optional[int] = None
_submenu_ent: Optional[int] = None


def create_node(key: str, label: str, parent: Optional[str] = None, background: bool = False, components=()) -> int:
    """Registers a node and returns its entity id. If `parent` is given, the
    new key is appended to the parent's children list. `components` lets a
    leaf with exactly one visual widget (a MenuState list, say) attach it
    directly to the node's own entity instead of a separate OwnedBy entity."""
    ent = esper.create_entity(Node(key=key, parent=parent, background=background), *components)
    NODES[key] = ent
    LABELS[key] = label
    if parent:
        parent_node = esper.component_for_entity(NODES[parent], Node)
        parent_node.children.append(key)
    return ent


def resolve_leaf(key: str) -> str:
    """Walks down from `key` through remembered active_child indices until it
    reaches a node with no children."""
    node = esper.component_for_entity(NODES[key], Node)
    while node.children:
        index = node.active_child if 0 <= node.active_child < len(node.children) else 0
        key = node.children[index]
        node = esper.component_for_entity(NODES[key], Node)
    return key


def _path_to_root(key: str) -> list:
    parts = key.split(".")
    return [".".join(parts[:i + 1]) for i in range(len(parts))]


def _owned_entities(node_key: str):
    return [ent for ent, owned in esper.get_component(OwnedBy) if owned.node == node_key]


def _set_active(node_key: str, active: bool):
    node_ent = NODES[node_key]
    node = esper.component_for_entity(node_ent, Node)
    targets = [node_ent] + _owned_entities(node_key)

    for ent in targets:
        if active:
            if not esper.has_component(ent, Active):
                esper.add_component(ent, Active())
            if not esper.has_component(ent, Running):
                esper.add_component(ent, Running())
            dirty = esper.try_component(ent, Dirty)
            if dirty is not None:
                dirty.state = max(dirty.state, 1)
        else:
            if esper.has_component(ent, Active):
                esper.remove_component(ent, Active)
            if not node.background and esper.has_component(ent, Running):
                esper.remove_component(ent, Running)


def _update_chrome(top_key: str):
    # Narrows _header_ent/_submenu_ent from Optional[int] to int for the type
    # checker -- both are always set by init_modules() before switch_node()
    # (and therefore _update_chrome) can ever be called.
    assert _header_ent is not None and _submenu_ent is not None

    # boot isn't a navigable tab (see TOP_LEVEL) -- hide the shared chrome
    # entirely while it's the active top-level, matching the old BaseModule
    # system's boot module (no Header at all, submenu explicitly hidden).
    if top_key == "boot":
        if esper.has_component(_header_ent, Active):
            esper.remove_component(_header_ent, Active)
        if esper.has_component(_submenu_ent, Active):
            esper.remove_component(_submenu_ent, Active)
        return

    if not esper.has_component(_header_ent, Active):
        esper.add_component(_header_ent, Active())
    if not esper.has_component(_submenu_ent, Active):
        esper.add_component(_submenu_ent, Active())

    header_state = esper.component_for_entity(_header_ent, HeaderState)
    header_state.label = LABELS[top_key]
    esper.component_for_entity(_header_ent, Dirty).state = 1

    node = esper.component_for_entity(NODES[top_key], Node)
    submenu_state = esper.component_for_entity(_submenu_ent, SubMenuState)
    submenu_state.options = [LABELS[c] for c in node.children]
    submenu_state.active_index = max(node.active_child, 0)
    esper.component_for_entity(_submenu_ent, Dirty).state = 1


def switch_node(key: str):
    """Activates the node at `key` (and every ancestor down to it), remembers
    it as each ancestor's active_child, and deactivates whatever was active
    before that isn't on the new path. `key` should normally be a leaf --
    callers that only know a top-level tab should go through resolve_leaf()
    first (see handle_action())."""
    global ACTIVE_LEAF

    if key not in NODES:
        raise Exception(f"Node {key!r} not registered")

    new_path = _path_to_root(key)
    old_path = _path_to_root(ACTIVE_LEAF) if ACTIVE_LEAF else []

    common = 0
    while common < len(old_path) and common < len(new_path) and old_path[common] == new_path[common]:
        common += 1

    for node_key in reversed(old_path[common:]):
        _set_active(node_key, False)
        esper.dispatch_event("node_paused", node_key)

    for depth in range(common, len(new_path)):
        node_key = new_path[depth]
        _set_active(node_key, True)
        if depth > 0:
            parent_key = new_path[depth - 1]
            parent_node = esper.component_for_entity(NODES[parent_key], Node)
            parent_node.active_child = parent_node.children.index(node_key)
        esper.dispatch_event("node_resumed", node_key)

    ACTIVE_LEAF = key
    _update_chrome(new_path[0])


def switch_module(top_key: str):
    """Switches to a top-level tab, descending to its remembered leaf."""
    switch_node(resolve_leaf(top_key))


def _find_menu_entity(node_key: str) -> Optional[int]:
    node_ent = NODES[node_key]
    if esper.has_component(node_ent, MenuState):
        return node_ent
    for ent in _owned_entities(node_key):
        if esper.has_component(ent, MenuState):
            return ent
    return None


def _dispatch_menu_action(action: str):
    if not ACTIVE_LEAF:
        return
    ent = _find_menu_entity(ACTIVE_LEAF)
    if ent is None:
        return
    menu_state = esper.component_for_entity(ent, MenuState)
    if menu_handle_action(menu_state, action):
        dirty = esper.try_component(ent, Dirty)
        if dirty is not None:
            dirty.state = 1
        if menu_state.on_change:
            menu_state.on_change(menu_state.selected)


def handle_action(action: str):
    if action.startswith("module_"):
        top_key = action[len("module_"):]
        if top_key in NODES:
            switch_module(top_key)
        else:
            logger.debug(f"No module registered for action {action!r}")
    elif action.startswith("knob_"):
        if not ACTIVE_LEAF:
            return
        top_key = _path_to_root(ACTIVE_LEAF)[0]
        node = esper.component_for_entity(NODES[top_key], Node)
        index = int(action[-1]) - 1
        if 0 <= index < len(node.children):
            switch_node(resolve_leaf(node.children[index]))
        else:
            logger.debug(f"No submodule ({index}) on [{top_key}]")
    elif action in ("dial_up", "dial_down"):
        _dispatch_menu_action(action)


def init_modules(pipboy):
    """Registers every top-level module and its children. Local imports (not
    at module scope) so that game/modules/<name>/__init__.py can safely do
    `from game.modules.registry import create_node` at its own module scope
    -- by the time this function actually runs (from PipBoy.__init__), this
    registry module has already finished importing."""
    global _header_ent, _submenu_ent

    logger.debug("Initializing Modules")

    # handle_action is a module-level function (not a local closure), so the
    # weak reference esper.set_handler keeps is safe -- this module stays
    # imported (and the function alive) for the life of the process.
    esper.set_handler("action", handle_action)

    _header_ent = esper.create_entity(
        Position(UI_MARGIN, 0), Renderable(), Layer(20), Dirty(1), HeaderState(), Active(),
    )
    _submenu_ent = esper.create_entity(
        Position(80, 54), Renderable(), Layer(20), Dirty(1), SubMenuState(), Active(),
    )

    from game.modules.boot import register as register_boot
    from game.modules.stat import register as register_stat
    from game.modules.inv import register as register_inv
    from game.modules.data import register as register_data
    from game.modules.map import register as register_map
    from game.modules.radio import register as register_radio

    # Real work, run one task per frame by boot/loading.py while its screen
    # is up (or all at once if SKIP_INTRO -- see PipBoy.init_modules()), not
    # eagerly here. Header options below are derived from TOP_LEVEL directly
    # (not the per-node LABELS dict) since these tasks -- and the LABELS
    # entries they create -- haven't run yet at this point.
    tasks = [
        ("Loading STAT...", lambda: register_stat(pipboy)),
        ("Loading INV...", lambda: register_inv(pipboy)),
        ("Loading DATA...", lambda: register_data(pipboy)),
        ("Loading MAP...", lambda: register_map(pipboy)),
        ("Loading RADIO...", lambda: register_radio(pipboy)),
    ]
    register_boot(pipboy, tasks)

    header_state = esper.component_for_entity(_header_ent, HeaderState)
    header_state.options = [key.upper() for key in TOP_LEVEL]
    header_state.label = header_state.options[0]

    return tasks
