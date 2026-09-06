# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A pygame-ce recreation of Fallout 4's Pip-Boy 3000 Mk IV, built to run on a Raspberry Pi (GPIO buttons + small display) and also on desktop (keyboard) for development. Currently on branch `rework`, a from-scratch rewrite of an older, now-deleted prototype.

**In-progress rewrite**: an approved architecture-overhaul plan is being implemented in phases. Phases 0-5 are done: config/`.env` fixes, a JSON save-data store + item catalog, an ECS core (using `esper`), state-based UI widgets, and a generic Node registry that replaced the old `BaseModule`/`SubModule` sprite system entirely (that system, along with `core.engine.Entity`/`EntityGroup`, no longer exists in this codebase). Remaining: Phase 6 (GPIO → `gpiozero`, N-tier input dispatch) and Phase 7 (real boot sequence content). The full phased plan is kept in the project owner's local Claude Code plan history, not in this repo. The Architecture section below describes the current (post-Phase-5) state.

## Commands

```
uv sync                 # install dependencies (first run / after pulling changes)
uv run python main.py   # run the app
```

Pi-only GPIO dependencies are an optional extra once added: `uv sync --extra pi`.

There is no test suite, linter, or CI configured in this repository.

## Architecture (current, post-Phase-5 state)

**Entry point**: `main.py` initializes `pg.mixer`, constructs `PipBoy` (`game/pipboy.py`) with `config.SIZE`/`config.OUTPUT_SIZE`, and calls `.run()`. It also sets Pi-specific SDL env vars (framebuffer/touchscreen) when `config.GPIO_AVAILABLE` is true.

**Engine layer** (`core/engine.py`): `Engine` is a thin wrapper around `esper`'s default world. `update(dt)` calls `esper.process(dt)`; `render()` calls `RenderProcessor.process()` then flips the display, skipping the flip entirely on frames where nothing changed (`RenderProcessor.dirty_this_frame`) — a battery optimization for the Pi Zero 2 W target. There is no sprite-group/`Entity` base class anymore; everything is plain esper components on plain entities (`core/components.py`). `core/resource_loader.py`'s `ResourceLoader` is a static, non-instantiable cache-by-key loader for images/sounds/fonts (paths are relative to `config.ASSETS_FOLDER`).

**Rendering pipeline** (`core/processors.py`): `TweenProcessor` (priority 50), `AnimationProcessor` (40), `AutoScrollProcessor` (35), `UIRenderProcessor` (30, in `game/ui.py` — rebuilds a widget's `Renderable.image` from its `*State` component when `Dirty.state >= 1`), then `RenderProcessor` (invoked directly from `Engine.render()`, not an `esper.Processor`) composites every `Active`, visible `(Position, Renderable, Layer)` entity onto the screen in layer order using **additive blending** (`pg.BLEND_RGBA_ADD`) — this matches the app's CRT-glow look and is why any standalone text/image must be pre-flattened onto an opaque background before becoming a `Renderable.image` (see `game/ui.py`'s `render_text` and its docstring) rather than left with a transparent, anti-aliased edge.

**Module tree** (`game/modules/registry.py`): a single recursive `Node` concept (`core/components.py`) replaced the old `BaseModule`/`SubModule` split — a node is a top-level tab, a submodule, or (unused by any real content yet, but supported) a level below that; depth is just how many `Node.parent` links you follow. `NODES: dict[key, entity_id]` and `LABELS: dict[key, str]` index the tree. A node's own entity may carry visual components directly (a leaf with one widget) or own separate entities tagged `OwnedBy(node.key)` (a leaf with several, e.g. `stat.status`'s footer + vault-boy animation + health bars). `switch_node(key)` activates a node and its ancestors (deactivating whatever was active before), remembers each ancestor's `active_child`, and updates the shared Header/SubMenu chrome entities. A node with `background=True` (only `radio`/`radio.stations` today) keeps its `Running` tag after losing `Active`, so a processor gated on `Running` instead of `Active` keeps executing while a different tab is shown (see `game/modules/radio/__init__.py`'s `_RadioTickProcessor` — no real audio yet, see the plan's "Explicitly out of scope"). `PipBoy.handle_action` forwards every action to `registry.handle_action`, which handles `module_*` (switch top-level tab, descending to the remembered leaf), `knob_N` (switch within the active top-level), and `dial_up`/`dial_down` (forwarded to the active leaf's `MenuState`, if it has one).

Each top-level package (`game/modules/{stat,inv,data,map,radio,boot}/`) exposes a module-level `register(pipboy)` called from `registry.init_modules()`. `boot`'s three children are registered but structural-only (no content, unreachable) until Phase 7.

**UI widgets** (`game/ui.py`): `HeaderState`/`SubMenuState`/`FooterState`/`MenuState`/`ProgressBarState` dataclasses plus matching `render_*` pure functions and `UIRenderProcessor`. `FooterState.update_section(index, value)` and `menu_handle_action(state, action)` (`dial_up`/`dial_down`) are the two pieces of behavior still attached to a state object; everything else is a plain redraw. Mutating a `*State` in place does nothing by itself — the mutator must also arm the entity's `Dirty.state = 1`.

**Config** (`utils/settings.py`): a `pydantic-settings` `ConfigSettings` singleton (`config`), instantiated once at import time, `.env`-backed. `SAVE_FILE`, `IDLE_FRAMERATE`, `STARTUP_MODULE` control persistence/battery/boot behavior. GPIO pin availability is detected via a `try: import RPi.GPIO` cached property (`config.GPIO_AVAILABLE`) — still `RPi.GPIO`-based polling (`PipBoy.check_gpio_input()`) until Phase 6 moves it to `gpiozero`.

**Persistence** (`game/data/store.py`, `game/data/catalog.py`): `save_data: SaveData` (theme, player status, inventory, perks, quests, workshops, location) loads from `config.SAVE_FILE` (`save/state.json`, gitignored; `save/state.example.json` is the tracked, hand-editable reference) at import time and autosaves every 30s plus on clean exit (`game/pipboy.py`). `catalog.py` loads every `assets/data/*.json` into `dict[baseid, item]` at import time. `theme` (also `game/data/store.py`) holds the RGB-converted draw/tint/bg colors read by `game/ui.py`'s render functions.
