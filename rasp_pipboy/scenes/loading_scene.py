import pygame as pg
import os
from rasp_pipboy.core.scene_base import SceneBase
from rasp_pipboy.core.resource_loader import ResourceLoader
from rasp_pipboy.utils.config import ConfigSettings
from rasp_pipboy.core.events import CURSOR_COOLDOWN, TYPING_COOLDOWN, INTRO_FINISHED, LOADING_CONTENT
from rasp_pipboy.components.fading_text import FadingText
from rasp_pipboy.components.animated_sprite import AnimatedSprite
from rasp_pipboy.components.progress_bar import ProgressBar
from rasp_pipboy.utils.calc import calculate_center
from rasp_pipboy.scenes.stats_scene import StatsScene
from rasp_pipboy.scenes.inventory_scene import InventoryScene
from rasp_pipboy.scenes.data_scene import DataScene
from rasp_pipboy.scenes.map_scene import MapScene
from rasp_pipboy.scenes.radio_scene import RadioScene
import threading


class IntroAnimation(SceneBase):
    def __init__(self):
        super().__init__()
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
        self.surf_size = (font_size[0] * 73, font_size[1] * 104)

        self.GAME_STATE = 0
        self.boot_text_surface = font.render(
            boot_text, True, pg.Color("white"))
        self.velocity = self.surf_size[1] / 3
        self.position_y = ConfigSettings().height
        self.text_pos = [0, 0, 0]

        font = ResourceLoader.getInstance().get_font("MONOFONTO", 16)
        cursor_size = font.size(' ')
        self.cursor = pg.Rect(0, 0, cursor_size[0], cursor_size[1])

        self.boot2_text_surface = pg.Surface(
            (cursor_size[0] * 49, cursor_size[1] * 11), pg.SRCALPHA)
        self.boot3_text_surface = self.boot2_text_surface.copy()

        ResourceLoader.getInstance().play_sound('boot_a')
        self.show_cursor = False
        self.cursor_counter = 8
        self.boot_3_pos_y = 0
        self.timer_up = 6

    def process_input(self, events, keys):
        for event in events:
            if CURSOR_COOLDOWN == event.type:
                if self.GAME_STATE <= 3:
                    self.show_cursor = not self.show_cursor
                else:
                    self.show_cursor = False
                    pg.time.set_timer(CURSOR_COOLDOWN, 0)
                self.cursor_counter -= 1
                if self.GAME_STATE == 3:
                    if self.timer_up <= 0:
                        self.GAME_STATE = 4
                    else:
                        self.timer_up -= 1

            elif TYPING_COOLDOWN == event.type:
                if self.GAME_STATE == 2:
                    if (self.text_pos[2] < len(self.loader_text)):
                        c = self.loader_text[self.text_pos[2]]
                        if c == "\n":
                            self.text_pos[0] = 0
                            self.text_pos[1] += 1
                        else:
                            self.text_pos[0] += 1
                        self.draw_boot_text()
                        self.text_pos[2] += 1
                    else:
                        self.GAME_STATE = 3
                        pg.time.set_timer(TYPING_COOLDOWN, 0)

    def draw_cursor(self, position):
        if not self.show_cursor:
            return
        self.cursor.left = position[0] * self.cursor.width
        self.cursor.top = position[1] * self.cursor.height
        if self.GAME_STATE >= 2 or self.GAME_STATE <= 4:
            self.cursor.left += self.cursor.width
        pg.draw.rect(self.boot2_text_surface, (255, 255, 255), self.cursor)

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
                pg.time.set_timer(TYPING_COOLDOWN, 20)
                ResourceLoader.getInstance().play_sound('boot_b')
        elif self.GAME_STATE == 4 and self.timer_up <= 0:
            self.boot_3_pos_y -= (self.cursor.height * 22) * dt
            if self.boot_3_pos_y <= -self.boot2_text_surface.get_height():
                self.GAME_STATE = 5
                pg.time.delay(200)
                event = pg.event.Event(INTRO_FINISHED)
                pg.event.post(event)

    def draw_boot_text(self):
        c = self.loader_text[self.text_pos[2]]
        font = ResourceLoader.getInstance().get_font("MONOFONTO", 16)
        text_surface = font.render(c, True, (255, 255, 255))
        self.boot3_text_surface.blit(
            text_surface, (self.text_pos[0]*text_surface.get_width(), self.text_pos[1] * text_surface.get_height()))

    def render(self, render):
        super().render(render)
        if self.GAME_STATE == 0:
            render.blit(self.boot_text_surface, (ConfigSettings(
            ).width / 2 - self.boot_text_surface.get_width() / 2, self.position_y))
        elif self.GAME_STATE >= 1 and self.GAME_STATE <= 4:
            self.boot2_text_surface.fill((255, 255, 255, 0))
            self.boot2_text_surface.blit(
                self.boot3_text_surface, (0, self.boot_3_pos_y))
            if self.show_cursor:
                self.draw_cursor(self.text_pos)
            render.blit(self.boot2_text_surface, (ConfigSettings(
            ).width / 2 - self.boot2_text_surface.get_width() / 2, 0))

    def terminate(self):
        ResourceLoader.getInstance().remove_sound("boot_a")
        ResourceLoader.getInstance().remove_sound("boot_b")


class InitializeAnimation(SceneBase):

    def __init__(self):
        super().__init__()
        ResourceLoader.getInstance().add_sound("boot_c", 'sounds/boot/c.ogg')
        ResourceLoader.getInstance().add_sound("boot_d", 'sounds/boot/d.ogg')
        ResourceLoader.getInstance().add_music('humming' , os.path.join('sounds', 'UI_PipBoy_Hum_LP.wav'))
        font = ResourceLoader.getInstance().get_font("MONOFONTO", 12)
        self.fading_text = FadingText("INITIALIZING...", font)
        self.vault_boy = AnimatedSprite(False, False, 0.1)

        images = []
        for i in range(1, 8):
            path = os.path.join(ConfigSettings().assets_folder,
                                "img", "boot", "vault_boy_"+str(i)+".png")
            image = pg.image.load(path).convert_alpha()
            image = pg.transform.smoothscale(
                image, (int(image.get_width()/2), int(image.get_height()/2)))
            images.append(image)
        self.vault_boy.set_images(images)

        self.GAME_STATE = 0
        self.pos = calculate_center(
            ConfigSettings().size, self.vault_boy.rect.size)
        self.surface = pg.Surface(ConfigSettings().size, pg.SRCALPHA)
        bg_surface = self.surface.copy()
        bg_surface.fill((0,0,0))
        self.initialize = pg.sprite.LayeredDirty()
        self.initialize.add(self.fading_text)
        self.initialize.add(self.vault_boy)
        self.initialize.clear(self.surface, bg_surface)
        self.vault_boy.rect.x = self.pos[0] - 20
        self.vault_boy.rect.y = self.pos[1]
        self.fading_text.rect.x = ConfigSettings().width/2 - self.fading_text.rect.width/2
        pos = self.pos[1] + self.vault_boy.rect.height + 20
        self.fading_text.rect.y = pos
        self.progress_bar = ProgressBar(pg.Rect(
            ConfigSettings().width/4,
            pos + 20,
            ConfigSettings().width/2,
            20),
            font
        )
        self.initialize.add(self.progress_bar)
        ResourceLoader.getInstance().play_music('humming')
        

    def load_files(self):
        self.progress_bar.set_max_value(5)
        self.parent.parent.add_entity("stats_screen", StatsScene(), False)
        self.progress_bar.add_value()
        self.parent.parent.add_entity("inv_screen", InventoryScene(), False)
        self.progress_bar.add_value()
        self.parent.parent.add_entity("data_screen", DataScene(), False)
        self.progress_bar.add_value()
        self.parent.parent.add_entity("map_screen", MapScene(), False)
        self.progress_bar.add_value()
        self.parent.parent.add_entity("radio_scene", RadioScene(), False)
        self.progress_bar.add_value()
        self.GAME_STATE = 1

    def process_input(self, events, keys):
        super().process_input(events, keys)
        for event in events:
            if event.type == LOADING_CONTENT:
                pg.time.set_timer(LOADING_CONTENT, 0)
                self.thread_load_files = threading.Thread(
                    target=self.load_files)
                self.thread_load_files.start()

    def on_show(self):
        ResourceLoader.getInstance().play_sound("boot_c")
        pg.time.set_timer(LOADING_CONTENT, 200)

    def update(self, dt: float):
        self.initialize.update(dt)
        if self.GAME_STATE == 1:
            self.GAME_STATE = 2
            self.vault_boy.play()
        if self.GAME_STATE == 2 and self.vault_boy.finished:
            self.GAME_STATE = 3
            ResourceLoader.getInstance().play_sound("boot_d")

    def render(self, render: pg.Surface):
        self.initialize.draw(self.surface)
        render.blit(self.surface, (0, -30))


class LoadingScene(SceneBase):

    def __init__(self):
        super().__init__()
        # self.add_entity("intro_anim", IntroAnimation())
        self.add_entity("init", InitializeAnimation())
        self.get_entity("init").on_show()

    def initialize(self):
        pass

    def update(self, dt: float):
        super().update(dt)

    def process_input(self, events, keys):
        super().process_input(events, keys)

        for event in events:
            if event.type == INTRO_FINISHED:
                self.remove_entity("intro_anim")
                self.show_entity("init")
