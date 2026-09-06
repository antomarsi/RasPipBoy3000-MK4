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
    if action.startswith("knob_"):
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
