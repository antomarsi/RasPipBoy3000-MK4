import esper

from core.components import Dirty, Layer, OwnedBy, Position, Renderable, Tween
from core.resource_loader import ResourceLoader
from game.data.store import theme
from game.modules.registry import create_node, switch_node
from utils.settings import config

NODE_KEY = "boot.boot_text"
_VELOCITY = 500.0  # px/s
_HANDLERS = {}

_LINES = [
    "1 0 0x000A4 0x00000000000000000 start memoty discovery 0 0x0000A4",
    "0x00000000000000000 1 0 0x000014 0 0x00000000000000000 CPUO starting cell",
    "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009",
    "0x00000000000000000 CPUD launch EFI0 0x0000A4 0x00000000000000000 1 0",
    "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4",
    "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory",
    "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000",
    "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014",
    "0x00000000000000000 CPUO stating cell relocation0 0x0000A4",
    "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0",
    "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO",
    "stating EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4",
    "0x00000000000000000 start memory discovery 0 0x0000A4 0x00000000000000000",
]


def _build_text_image(color, bg_color):
    lines = _LINES * 8
    lines[0] = f"* {lines[0]}"
    font = ResourceLoader.get_font("MONOFONTO", 12)
    return font.render("\n".join(lines), True, color, bg_color).convert_alpha()


def register(pipboy):
    create_node(NODE_KEY, "", parent="boot")

    sound = ResourceLoader.add_sound("boot_chime", "sounds/boot/boot.ogg") if config.SOUND_ENABLED else None

    image = _build_text_image(theme.draw_color, theme.bg_color)
    start_y = float(config.HEIGHT)
    end_y = -(image.get_height() * 1.3)
    duration = (start_y - end_y) / _VELOCITY
    x = config.WIDTH / 2 - image.get_width() / 2

    text_ent = esper.create_entity(
        Position(x, start_y), Renderable(image=image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))

    def on_resumed(key):
        if key != NODE_KEY:
            return
        if sound:
            sound.play()
        position = esper.component_for_entity(text_ent, Position)
        position.y = start_y
        esper.add_component(text_ent, Tween(
            start=start_y, end=end_y, duration=duration,
            apply=lambda v: setattr(position, "y", v),
            on_complete=lambda: switch_node("boot.loading"),
        ))

    def on_paused(key):
        if key != NODE_KEY:
            return
        if sound:
            sound.stop()
        if esper.has_component(text_ent, Tween):
            esper.remove_component(text_ent, Tween)

    _HANDLERS[NODE_KEY] = (on_resumed, on_paused)
    esper.set_handler("node_resumed", on_resumed)
    esper.set_handler("node_paused", on_paused)
