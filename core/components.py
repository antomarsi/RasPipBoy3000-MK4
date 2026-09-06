from dataclasses import dataclass, field
from typing import Callable, Optional

import pygame as pg


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Layer:
    order: int = 0


@dataclass
class Renderable:
    image: Optional[pg.Surface] = None
    visible: bool = True


@dataclass
class Dirty:
    """0 = clean, 1 = redraw once (re-armed by whatever mutates the entity's
    own state), 2 = always redraw (perpetual-motion entities like Scanlines)."""
    state: int = 1


@dataclass
class Active:
    """Tag: presence means this entity is currently visible/rendered and
    receiving input."""


@dataclass
class Running:
    """Tag: presence means this entity's non-visual processors keep executing
    even while it is not Active (e.g. a backgrounded module's audio state)."""


@dataclass
class AnimationState:
    frames: list = field(default_factory=list)
    duration_per_frame: float = 0.2
    elapsed: float = 0.0
    current_frame: int = 0
    loop: bool = False
    playing: bool = False
    finished: bool = False
    on_complete: Optional[Callable[[], None]] = None


@dataclass
class Tween:
    start: float
    end: float
    duration: float
    apply: Callable[[float], None]
    easing: Optional[Callable[[float], float]] = None
    elapsed: float = 0.0
    on_complete: Optional[Callable[[], None]] = None
    playing: bool = True


@dataclass
class AutoScroll:
    speed: float = 100.0
    min_y: float = -130.0
    max_y: float = 540.0


@dataclass
class Node:
    """A node in the module tree: a top-level tab, a submodule, or (not
    exercised by any real content yet) a level below that. Depth is just how
    many `parent` links you follow -- there is no separate "module" vs
    "submodule" type. See game/modules/registry.py."""
    key: str
    parent: Optional[str] = None
    children: list = field(default_factory=list)
    active_child: int = -1
    background: bool = False


@dataclass
class OwnedBy:
    """Tags a visual entity as belonging to a Node, so switch_node() can
    activate/deactivate every entity a node owns as a group without each one
    needing to be the Node's own entity."""
    node: str
