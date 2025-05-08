from core.engine import Entity
from core.resource_loader import ResourceLoader
from game.modules import SubModule
from utils.settings import config
import pygame as pg

from utils.events import BOOT_EVENT


class Module(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)
        self.boot_text = BootText()
        self.sound = ResourceLoader.add_sound("boot_a", 'sounds/boot/a.ogg')

    def handle_resume(self):
        self.add(self.boot_text)
        self.sound.play()
        return super().handle_resume()

    def handle_pause(self):
        self.boot_text.kill()
        self.sound.stop()
        return super().handle_pause()


class BootText(Entity):
    def __init__(self, color=config.DRAW_COLOR, bg_color=config.BG_COLOR, *args, **kwargs):
        super().__init__((config.WIDTH, config.HEIGHT), *args, **kwargs)
        self.bg_color = bg_color

        boot_text = [
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
            "0x00000000000000000 start memory discovery 0 0x0000A4 0x00000000000000000"]
        text = []
        for _ in range(0, 8):
            for t in boot_text:
                text.append(t)
        boot_text = text
        del text
        boot_text[0] = f"* {boot_text[0]}"
        boot_text = "\n".join(boot_text)
        font = ResourceLoader.get_font("MONOFONTO", 12)
        self.image = font.render(boot_text, True, color, self.bg_color).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = config.WIDTH/2
        self.rect.top = config.HEIGHT
        self.velocity = 500

    def update(self, deltatime, *args, **kwargs):
        self.rect.top -= self.velocity * deltatime
        if self.rect.top <= -(self.rect.height * 1.3):
            pg.event.post(pg.event.Event(BOOT_EVENT, {"scene": 1}))
        return super().update(deltatime, *args, **kwargs)
