from core.engine import AnimatedSprite, Entity
from core.resource_loader import ResourceLoader
from game.modules import SubModule
from game.ui import Footer, ProgressBar
from utils.settings import config
import pygame as pg


class Module(SubModule):

    def __init__(self, parent, *sprites, **kwargs):
        super().__init__(parent, *sprites, **kwargs)
        progressbar = ProgressBar(
            (200, 29), value=26, max_value=100, border_width=2, margin=(0, 4, 0, 4))
        self.footer = Footer(
            ["HP 90/100", [["LEVEL 120", progressbar], 2], "AP 90/90"])
        self.health = HealthContainer()
        self.stimpak = BottomTextContainer("Stimpak")
        self.radaway = BottomTextContainer("Radaway")

        self.stimpak.rect.topleft = [50, config.HEIGHT - 79]
        self.radaway.rect.topleft = [
            50 + self.stimpak.rect.width + 14, config.HEIGHT - 79]

        self.pipboy_anim = PipBoyHealthAnim()
        self.pipboy_anim.rect.center = (
            config.WIDTH * 0.5, config.HEIGHT * 0.45)

        self.add(self.pipboy_anim)
        self.add(self.stimpak)
        self.add(self.radaway)
        self.add(self.health)
        self.add(self.footer)

    def __str__(self):
        return "STATUS"


class PipBoyHealthAnim(Entity):

    drugged = False
    radiation = False

    head_wounded = False
    left_arm_wounded = False
    left_leg_wounded = False
    right_arm_wounded = False
    right_leg_wounded = False

    def __init__(self, color=config.DRAW_COLOR, bg_color=config.BG_COLOR):
        super().__init__()
        self.color = color
        self.bg_color = bg_color

        self.duration_per_frame = 0.2
        self.start_frame = 0

        self.current_anim_index = 0
        self.body = [ResourceLoader.add_image(
            f"body_ok_0_{x}", f"images/health_cond/icon_condition_body_0_{x}.png") for x in range(0, 8)]
        self.head = ResourceLoader.add_image(
            f"head_ok_0", f"images/health_cond/head_normal.png")
        self.image = pg.Surface(
            (self.body[0].get_width(), self.body[0].get_height() + self.head.get_height()))
        self.rect = self.image.get_rect()
        self.body_top = self.rect.height - self.body[0].get_height()

        self.timer = 0
        self.render()

    def render(self):
        self.image.fill(self.bg_color)
        self.image.blit(self.head, (27, 10))
        self.image.blit(self.body[self.current_anim_index], (0, self.body_top))
        self.image.fill(self.color, special_flags=pg.BLEND_MULT)
        self.dirty = 1

    def update(self, deltatime=0):
        self.timer += deltatime
        new_frame = int(self.timer * 10) % len(self.body)
        if new_frame != self.current_anim_index:
            self.current_anim_index = new_frame
            self.render()



class HealthContainer(Entity):
    def __init__(self):
        super().__init__((config.WIDTH * 0.8, config.HEIGHT - 172))
        self.rect.top = 92
        self.rect.left = config.WIDTH * 0.1
        self.body_part_position = {
            # "head":  ,
            # "left_arm": 1,
            # "right_arm": 1,
            # "left_leg": 1,
            # "right_leg": 1
        }
        self.init_body_parts()
        self.render()

    def init_body_parts(self):
        # Head
        self.body_part_position["head"] = ProgressBar(
            (32, 9), value=100, max_value=100, border_width=1)
        self.body_part_position["head"].rect.centerx = self.image.get_rect(
        ).centerx + 4
        self.body_part_position["head"].rect.top = self.image.get_height(
        ) * 0.06

        # Left Arm
        self.body_part_position["left_arm"] = ProgressBar(
            (32, 9), value=100, max_value=100, border_width=1)
        self.body_part_position["left_arm"].rect.centerx = self.image.get_rect(
        ).centerx * 0.63
        self.body_part_position["left_arm"].rect.top = self.image.get_height(
        ) * 0.3

        # Left Leg
        self.body_part_position["left_leg"] = ProgressBar(
            (32, 9), value=100, max_value=100, border_width=1)
        self.body_part_position["left_leg"].rect.centerx = self.image.get_rect(
        ).centerx * 0.63
        self.body_part_position["left_leg"].rect.top = self.image.get_height(
        ) * 0.61

        # Right Arm
        self.body_part_position["right_arm"] = ProgressBar(
            (32, 9), value=100, max_value=100, border_width=1)
        self.body_part_position["right_arm"].rect.centerx = self.image.get_rect(
        ).centerx * 1.38
        self.body_part_position["right_arm"].rect.top = self.image.get_height(
        ) * 0.3 + 1

        # Right Leg
        self.body_part_position["right_leg"] = ProgressBar(
            (32, 9), value=100, max_value=100, border_width=1)
        self.body_part_position["right_leg"].rect.centerx = self.image.get_rect(
        ).centerx * 1.38
        self.body_part_position["right_leg"].rect.top = self.image.get_height(
        ) * 0.61 + 1

        # Full
        self.body_part_position["full"] = ProgressBar(
            (32, 9), value=100, max_value=100, border_width=1)
        self.body_part_position["full"].rect.centerx = self.image.get_rect(
        ).centerx + 4
        self.body_part_position["full"].rect.top = self.image.get_height(
        ) * 0.72 + 14

    def render(self):
        global playerStatus

        for e in self.body_part_position.values():
            self.image.blit(e.image, e.rect.topleft)


class BottomTextContainer(Entity):
    def __init__(self, text: str, quantity=0, color=config.DRAW_COLOR):
        super().__init__()
        self.text = text.upper()
        self.font = ResourceLoader.get_font("MONOFONTO", 24)
        self._quantity = quantity
        self.bg_color = (color[0] * 0.75, color[1] * 0.75, color[2] * 0.75)
        self.color = (color[0] * 0.5, color[1] * 0.5, color[2] * 0.5)
        self.render()
        self.rect = self.image.get_rect()

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity
        self.render()

    def render(self):
        text = self.font.render(
            f"{self.text}({self.quantity})", True, self.color)
        self.image = pg.Surface((text.get_width() + 7, text.get_height()))
        self.image.fill(self.bg_color)
        self.image.blit(text, (4, -1))
        self.rect = self.image.get_rect()
        self.dirty = 1
