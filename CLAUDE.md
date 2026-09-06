# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A pygame-ce recreation of Fallout 4's Pip-Boy 3000 Mk IV, built to run on a Raspberry Pi (GPIO buttons + small display) and also on desktop (keyboard) for development. Currently on branch `rework`, a from-scratch rewrite of an older, now-deleted prototype.

**In-progress rewrite**: an approved architecture-overhaul plan is being implemented — migrating the module system from OOP `BaseModule`/`SubModule` sprite classes to an ECS (using `esper`), fixing the config/`.env` loading, adding a JSON save-data store, and moving GPIO handling to `gpiozero`. The plan lives at `C:\Users\antom\.claude\plans\i-want-to-make-sparkling-kitten.md`. Sections below describe the architecture as it exists in the code today — check whether a given file has been migrated yet before assuming either the old or new pattern applies.

## Commands

```
uv sync                 # install dependencies (first run / after pulling changes)
uv run python main.py   # run the app
```

Pi-only GPIO dependencies are an optional extra once added: `uv sync --extra pi`.

There is no test suite, linter, or CI configured in this repository.

## Architecture (current, pre-ECS-migration state)

**Entry point**: `main.py` initializes `pg.mixer`, constructs `PipBoy` (`game/pipboy.py`) with `config.SIZE`/`config.OUTPUT_SIZE`, and calls `.run()`. It also sets Pi-specific SDL env vars (framebuffer/touchscreen) when `config.GPIO_AVALIABLE` is true.

**Engine layer** (`core/engine.py`): `Engine` wraps a single `pygame.sprite.LayeredDirty` group (`EntityGroup`) and drives it every frame — `update(dt)` → `render()` (clear/draw the group, optionally rescale to `output_size`, then flip). `Entity(pygame.sprite.DirtySprite)` is the base class nearly every UI widget subclasses. `AnimatedSprite` is a generic frame-list player that currently isn't used by anything. `core/resource_loader.py`'s `ResourceLoader` is a static, non-instantiable cache-by-key loader for images/sounds/fonts (paths are relative to `config.ASSETS_FOLDER`).

**Module/submodule system** (`game/modules/__init__.py`, `game/pipboy.py`): `PipBoy` owns a `self.modules: dict[str, BaseModule]`, one per top-level tab (`boot`, `stat`, `inv`, `data`, `map`, `radio`). Each `BaseModule` owns a list of `SubModule` instances (its sub-tabs) and a `SubMenu` widget whose labels are auto-derived from `str(submodule)` — this is the one place labels aren't hand-duplicated elsewhere. `switch_module()`/`switch_submodule()` pause the old entity group, resume the new one, and add/remove it from the engine's render group. Input (`handle_action(action: str)`) flows from either a `pygame.KEYDOWN` matched against `config.ACTIONS`, or a per-frame GPIO pin poll (`PipBoy.check_gpio_input()`) matched against `config.GPIO_ACTIONS`, into the same dispatch chain: `PipBoy.handle_action` → active `BaseModule.handle_action` → active `SubModule.handle_action`.

Top-level module identity (which tabs exist, their display labels, and their keyboard/GPIO switch bindings) is **not** centralized — it's independently duplicated across `game/pipboy.py`'s import list + `modules` dict, and `utils/settings.py`'s `MODULE_TEXTS`/`GPIO_ACTIONS`/`ACTIONS`. A module's own `__str__()` must exactly string-match its `MODULE_TEXTS` entry or `Header.update_label()` (`game/ui.py`) raises `AttributeError`.

**UI widgets** (`game/ui.py`): `Header` (top tab bar), `SubMenu` (sub-tab row), `Footer` (bottom status bar, supports flexbox-like multi-section layout via `utils/layout.py`'s `layout_flex_row`), `Menu` (scrollable list, used by e.g. the radio station list), `ProgressBar`, `Scanlines`/`Overlay` (CRT effect). All render themselves into `self.image` on state change rather than through any shared render pipeline.

**Config** (`utils/settings.py`): a `pydantic-settings` `ConfigSettings` singleton (`config`), instantiated once at import time. **Known bug**: its custom env source (`MyCustomSource`) subclasses `EnvSettingsSource` instead of `DotEnvSettingsSource`, so `.env` is never actually read — only real OS environment variables take effect. GPIO pin availability is detected via a `try: import RPi.GPIO` cached property (`config.GPIO_AVALIABLE`, note the typo — used pervasively).

**Data models** (`game/data/`): `PlayerStatus` (`player.py`) is a pydantic model with hardcoded example values — no persistence exists yet. `assets/data/*.json` (`weapons`, `apparel`, `ammo`, `special`, `character`) are static catalog/example data, not currently loaded by any code path.

**Boot sequence** (`game/modules/boot/`): `boot_text.py` implements a working hex-scroll boot animation that posts a custom `BOOT_EVENT` (`utils/events.py`) on completion; `thumbs_up.py` and `pip_os.py` are empty stubs. `PipBoy.init_modules()` currently bypasses `boot` entirely and starts on `"map"`.
