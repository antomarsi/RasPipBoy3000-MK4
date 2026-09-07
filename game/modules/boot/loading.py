"""The loading screen: vault-boy frozen on frame 0 while real work happens
below it (registering every other top-level module), then plays its
thumbs-up animation once that work is done.

The task list passed to register() is the actual, real work being done --
each (label, callable) pair's callable is invoked for real, one per frame,
and the callable doesn't care whether it does local file I/O, decodes an
image, or (not built yet, but the shape supports it) fetches something over
the network. The progress bar and status text reflect that real work, not a
timer -- MIN_DURATION only pads the *end* of it so the screen doesn't flash
by while today's placeholder assets are still trivially small.
"""
import esper
import pygame as pg

from core.components import Active, AnimationState, Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game import audio
from game.data.store import theme
from game.modules.registry import create_node, switch_module
from game.ui import UI_MARGIN, ProgressBarState, render_text
from utils.settings import config

NODE_KEY = "boot.loading"
MIN_DURATION = 1.75  # seconds the screen stays up for once loading is done
_HANDLERS = {}


def _tint(source: pg.Surface, color) -> pg.Surface:
    # Source frames are white line art on a transparent background --
    # composite onto opaque black first, then BLEND_MULT-tint white -> theme
    # color (same technique as stat/status.py's vault-boy animation), since
    # RenderProcessor's additive-blend compositing needs an opaque, already
    # colored frame, not a raw alpha image.
    frame = pg.Surface(source.get_size())
    frame.blit(source, (0, 0))
    frame.fill(color, special_flags=pg.BLEND_MULT)
    return frame


def run_tasks_now(tasks):
    """Runs every loading task immediately and synchronously, with no visual
    feedback -- the config.SKIP_INTRO path still needs the real work (every
    other module's register(pipboy), which is what actually loads their
    assets) done before landing on the startup tab, it just never shows the
    animated loading screen `register()` below builds. Kept in this module
    rather than duplicated at the call site so there's exactly one place that
    knows how to run this task list."""
    for _, task in tasks:
        task()


def register(pipboy, tasks):
    """`tasks` is a list of (label, callable) pairs -- see
    registry.init_modules(), which builds it from every other top-level
    module's register(pipboy)."""
    node_ent = create_node(NODE_KEY, "", parent="boot")

    sound = ResourceLoader.add_sound("loading_loop", "sounds/boot/loading.ogg") if config.SOUND_ENABLED else None
    sound_channel = None

    raw_frames = [ResourceLoader.add_image(f"vault_boy_{i}", f"img/boot/vault_boy_{i}.png") for i in range(1, 9)]
    frames = [_tint(frame, theme.draw_color) for frame in raw_frames]
    vb_width, vb_height = frames[0].get_size()

    status_font = ResourceLoader.get_font("MONOFONTO", 24)
    status_height = status_font.get_height()
    bar_dimensions = (config.WIDTH * 0.6, 30)

    gap = 20
    total_height = vb_height + gap + status_height + gap + bar_dimensions[1]
    top = (config.HEIGHT - total_height) / 2

    vb_x = config.WIDTH / 2 - vb_width / 2
    vb_y = top
    status_y = vb_y + vb_height + gap
    bar_x = config.WIDTH / 2 - bar_dimensions[0] / 2
    bar_y = status_y + status_height + gap

    anim_ent = esper.create_entity(
        Position(vb_x, vb_y), Renderable(image=frames[0]), Layer(5), Dirty(1),
        AnimationState(frames=frames, duration_per_frame=0.15, loop=False, playing=False),
        OwnedBy(NODE_KEY))

    status_ent = esper.create_entity(
        Position(UI_MARGIN, status_y), Renderable(), Layer(5), Dirty(1), OwnedBy(NODE_KEY))

    bar_state = ProgressBarState(dimensions=bar_dimensions, value=0, max_value=max(len(tasks), 1), border_width=2)
    bar_ent = esper.create_entity(
        Position(bar_x, bar_y), Renderable(), Layer(5), Dirty(1), bar_state, OwnedBy(NODE_KEY))

    def set_status(text):
        image = render_text(status_font, text, theme.draw_color)
        # Center under the vault-boy regardless of label length.
        image_x = config.WIDTH / 2 - image.get_width() / 2
        esper.component_for_entity(status_ent, Position).x = image_x
        esper.component_for_entity(status_ent, Renderable).image = image
        esper.component_for_entity(status_ent, Dirty).state = 1

    state = {"tasks": list(tasks), "index": 0, "elapsed": 0.0, "phase": "loading"}

    def on_animation_complete():
        switch_module(config.STARTUP_MODULE)
        audio.start_hum()
        audio.play_startup()

    def on_resumed(key):
        nonlocal sound_channel
        if key != NODE_KEY:
            return
        state["index"] = 0
        state["elapsed"] = 0.0
        state["phase"] = "loading"
        bar_state.value = 0
        esper.component_for_entity(bar_ent, Dirty).state = 1
        anim = esper.component_for_entity(anim_ent, AnimationState)
        anim.current_frame = 0
        anim.elapsed = 0.0
        anim.playing = False
        anim.finished = False
        anim.on_complete = None
        esper.component_for_entity(anim_ent, Renderable).image = frames[0]
        esper.component_for_entity(anim_ent, Dirty).state = 1
        set_status("Loading...")
        if sound:
            sound_channel = sound.play(loops=-1)

    def on_paused(key):
        nonlocal sound_channel
        if key != NODE_KEY:
            return
        state["phase"] = "done"
        if sound_channel:
            sound_channel.stop()
            sound_channel = None

    _HANDLERS[NODE_KEY] = (on_resumed, on_paused)
    esper.set_handler("node_resumed", on_resumed)
    esper.set_handler("node_paused", on_paused)

    esper.add_processor(
        _LoadingProcessor(node_ent, state, bar_state, bar_ent, anim_ent, set_status, on_animation_complete),
        priority=25)


class _LoadingProcessor(esper.Processor):
    """Runs one task per frame while `boot.loading` is active -- real work,
    not a simulated fill -- then holds for MIN_DURATION once every task is
    done, then plays the vault-boy animation."""

    def __init__(self, node_ent, state, bar_state, bar_ent, anim_ent, set_status, on_animation_complete):
        self.node_ent = node_ent
        self.state = state
        self.bar_state = bar_state
        self.bar_ent = bar_ent
        self.anim_ent = anim_ent
        self.set_status = set_status
        self.on_animation_complete = on_animation_complete

    def process(self, dt):
        if not esper.has_component(self.node_ent, Active):
            return

        state = self.state
        state["elapsed"] += dt

        if state["phase"] == "loading":
            if state["index"] < len(state["tasks"]):
                label, task = state["tasks"][state["index"]]
                self.set_status(label)
                task()
                state["index"] += 1
                self.bar_state.value = state["index"]
                esper.component_for_entity(self.bar_ent, Dirty).state = 1
            else:
                state["phase"] = "waiting"
        elif state["phase"] == "waiting":
            if state["elapsed"] >= MIN_DURATION:
                state["phase"] = "playing"
                anim = esper.component_for_entity(self.anim_ent, AnimationState)
                anim.playing = True
                anim.on_complete = self.on_animation_complete
