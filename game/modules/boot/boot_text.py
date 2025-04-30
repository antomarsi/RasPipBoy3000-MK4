from core.engine import Entity
from core.resource_loader import ResourceLoader
from game.modules import SubModule
from utils.config import config


class Module(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)
        self.boot_text = BootText()
        self.add(self.boot_text)
        self.velocity = 10
        self.sound = ResourceLoader.add_sound("boot_a", 'sounds/boot/a.ogg')

    def handle_resume(self):
        self.sound.play()
        return super().handle_resume()

    def handle_pause(self):
        self.sound.stop()
        return super().handle_pause()

    def update(self, *args, **kwargs):
        if self.boot_text.finished:
            print("switching to submodule 1")
            self.parent.switch_submodule(1)
        return super().update(*args, **kwargs)


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
        self.text_texture = font.render(boot_text, True, color)
        self.position = [self.rect.centerx -
                         self.text_texture.get_width()/2, self.rect.bottom]
        self.velocity = 120
        self.finished = False

    def update(self, deltatime, *args, **kwargs):
        if not self.finished:
            self.position[1] -= self.velocity * deltatime
            if self.position[1] <= -(self.text_texture.get_height() * 1.2):
                self.finished = True
        return super().update(deltatime, *args, **kwargs)

    def render(self, *args, **kwargs):
        self.image.fill(self.bg_color)
        self.image.blit(self.text_texture, self.position)
