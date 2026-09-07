"""Ambient/UI sound effects that aren't tied to any single node: knob/dial
click sounds and the ambient Pip-Boy hum. Boot's own chime is loaded/played by
game/modules/boot/boot_text.py instead, since it's tied to that node's
activation.
"""
import esper

from components.sound_click import SoundClick
from core.resource_loader import ResourceLoader
from utils.settings import config

_hum_channel = None


def init():
    """Loads the knob/dial click sounds and subscribes to the "action" event
    (see game/modules/registry.py) so turning a knob or dial makes a sound.
    No-ops entirely if the mixer never initialized (config.SOUND_ENABLED)."""
    if not config.SOUND_ENABLED:
        return
    for path in SoundClick.rotaryHorizontal + SoundClick.rotaryVertical:
        ResourceLoader.add_sound(path, path)
    # _on_action is a module-level function, so the weak reference
    # esper.set_handler keeps is safe (this module stays imported for the
    # life of the process).
    esper.set_handler("action", _on_action)


def _on_action(action: str):
    # "Turning" actions -- GPIO's per-position knob buttons, keyboard's
    # module_* (1-5) top-level switch, and submodule_prev/next (Q/E) -- all
    # get the horizontal click; dial_up/dial_down (list scrolling) gets the
    # vertical one.
    if action.startswith("knob_") or action.startswith("module_") or action in ("submodule_prev", "submodule_next"):
        SoundClick.play_horizontal()
    elif action in ("dial_up", "dial_down"):
        SoundClick.play_vertical()


def start_hum():
    """Starts the looping ambient hum, once, if enabled. Config-only toggle
    (HUM_ENABLED) -- no runtime hotkey to mute it."""
    global _hum_channel
    if not config.SOUND_ENABLED or not config.HUM_ENABLED:
        return
    if _hum_channel is not None and _hum_channel.get_busy():
        return
    sound = ResourceLoader.add_sound("hum", "sounds/UI_PipBoy_Hum_LP.wav")
    _hum_channel = sound.play(loops=-1)


def play_startup():
    """Plays once, right when landing on the real startup tab -- whether
    that's the animated boot sequence finishing (boot/loading.py's
    on_animation_complete) or config.SKIP_INTRO skipping straight to it
    (PipBoy.init_modules()) -- both call this alongside start_hum()."""
    if not config.SOUND_ENABLED:
        return
    sound = ResourceLoader.add_sound("startup_chime", "sounds/boot/startup.ogg")
    sound.play()
