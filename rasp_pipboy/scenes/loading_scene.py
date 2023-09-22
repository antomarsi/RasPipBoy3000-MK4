import pygame as pg
from rasp_pipboy.core.scene_base import SceneBase
from rasp_pipboy.core.resource_loader import ResourceLoader
from rasp_pipboy.utils.config import ConfigSettings
from rasp_pipboy.core.events import CURSOR_COOLDOWN


class IntroAnimation(SceneBase):
    def __init__(self):
        super().__init__("Loading")
        ResourceLoader.getInstance().add_sound("boot_a", 'sounds/boot/a.ogg')
        ResourceLoader.getInstance().add_sound("boot_b", 'sounds/boot/b.ogg')

        self.loader_text = [
            "*************** PIP-OS(R) V7.1.08 ***************",
            "",
            "",
            "",
            "COPYRIGHT 2075 ROBCO(R)",
            "LOADER V1.1",
            "EXEC VERSION 41.10",
            "64k RAM SYSTEM",
            "38911 BYTES FREE",
            "NO HOLOTAPE FOUND",
            "LOAD ROM(1): DEITRIX 303"]
        self.loader_text = "\n".join(self.loader_text)

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
        for i in range(0, 8):
            for t in boot_text:
                text.append(t)
        boot_text = text
        boot_text[0] = f"* {boot_text[0]}"
        boot_text = "\n".join(boot_text)
        font = ResourceLoader.getInstance().get_font("MONOFONTO", 12)
        font_size = font.size(' ')
        surf_size = (font_size[0] * 73, font_size[1] * 104)
        
        self.GAME_STATE = 0
        self.boot_text_surface = font.render(boot_text, True, pg.Color("white"))
        self.velocity = surf_size[1] / 3
        self.position_y = ConfigSettings().height

        font = ResourceLoader.getInstance().get_font("MONOFONTO", 16)
        self.cursor_size = font.size(' ')

        #pg.time.delay(1500)
        ResourceLoader.getInstance().play_sound('boot_a')
        print(f"event: {CURSOR_COOLDOWN}")
        self.show_cursor = False
        self.cursor_counter = 4
        #ResourceLoader.getInstance().play_sound('boot_b')

    def process_input(self, events, keys):
        for event in events:
            if CURSOR_COOLDOWN == event.type:
                self.show_cursor = not self.show_cursor
                self.cursor_counter -= 1

    def draw_cursor(self, position: int):
        if not self.show_cursor:
            return
        
    
    def update(self, dt):
        super().update(dt)
        if self.GAME_STATE == 0:
            self.position_y -= self.velocity * dt
            if self.position_y < -self.boot_text_surface.get_height() - 100:
                self.GAME_STATE = 1
                pg.time.delay(100)
                pg.time.set_timer(CURSOR_COOLDOWN, 200)
                pg.time.delay(800)
        elif self.GAME_STATE == 1:
            if self.cursor_counter <= 0:
                self.GAME_STATE = 2
        elif self.GAME_STATE == 2:
            pass
            
    
    def render(self, render):
        super().render(render)
        if self.GAME_STATE == 0:
            render.blit(self.boot_text_surface, (ConfigSettings().width / 2 - self.boot_text_surface.get_width() / 2, self.position_y))
        elif self.GAME_STATE == 1 or self.GAME_STATE == 2:
            if self.show_cursor:
                self.cursor_rect.left = (
                    ConfigSettings().width/2 - self.surface_loader.get_width()/2) + self.cursor_rect_extra[1]
                self.cursor_rect.top = (
                    ConfigSettings().height/2 - self.surface_loader.get_height() / 2) + self.loader_y + self.cursor_rect_extra[0]
                pg.draw.rect(render, (255, 255, 255), self.cursor_rect)
            


class LoadingScene(SceneBase):

    def __init__(self):
        super().__init__("Loading")
        self.add_entity("intro_text", IntroAnimation())     

    def initialize(self):
        pass