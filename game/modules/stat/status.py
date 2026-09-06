import pygame as pg
import esper

from core.components import AnimationState, Dirty, Layer, OwnedBy, Position, Renderable
from core.resource_loader import ResourceLoader
from game.data.store import theme
from game.modules.registry import create_node
from game.ui import ProgressBarState, render_progressbar
from utils.settings import config

NODE_KEY = "stat.status"


def register(pipboy):
    create_node(NODE_KEY, "STATUS", parent="stat")
    _register_vaultboy_anim()
    _register_bottom_text()
    _register_health_bars()


def _build_vaultboy_frames(color):
    body_frames = [
        ResourceLoader.add_image(f"body_ok_0_{x}", f"images/health_cond/icon_condition_body_0_{x}.png")
        for x in range(8)
    ]
    head = ResourceLoader.add_image("head_ok_0", "images/health_cond/head_normal.png")
    body_w, body_h = body_frames[0].get_size()
    total_h = body_h + head.get_height()

    frames = []
    for body in body_frames:
        surface = pg.Surface((body_w, total_h))
        surface.blit(head, (27, 10))
        surface.blit(body, (0, total_h - body_h))
        surface.fill(color, special_flags=pg.BLEND_MULT)
        frames.append(surface)
    return frames


def _register_vaultboy_anim():
    frames = _build_vaultboy_frames(theme.draw_color)
    body_w, total_h = frames[0].get_size()
    x = config.WIDTH * 0.5 - body_w / 2
    y = config.HEIGHT * 0.45 - total_h / 2
    esper.create_entity(
        Position(x, y), Renderable(image=frames[0]), Layer(5), Dirty(2),
        AnimationState(frames=frames, duration_per_frame=0.1, loop=True, playing=True),
        OwnedBy(NODE_KEY))


def _render_bottom_text(font, text, quantity, color):
    bg_color = tuple(c * 0.75 for c in color)
    text_color = tuple(c * 0.5 for c in color)
    text_surface = font.render(f"{text.upper()}({quantity})", True, text_color)
    image = pg.Surface((text_surface.get_width() + 7, text_surface.get_height()))
    image.fill(bg_color)
    image.blit(text_surface, (4, -1))
    return image


def _register_bottom_text():
    font = ResourceLoader.get_font("MONOFONTO", 24)
    color = theme.draw_color

    stimpak_image = _render_bottom_text(font, "Stimpak", 0, color)
    stim_x, stim_y = 50, config.HEIGHT - 79
    esper.create_entity(Position(stim_x, stim_y), Renderable(image=stimpak_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))

    radaway_image = _render_bottom_text(font, "Radaway", 0, color)
    radaway_x = stim_x + stimpak_image.get_width() + 14
    esper.create_entity(Position(radaway_x, stim_y), Renderable(image=radaway_image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))


def _register_health_bars():
    left, top = config.WIDTH * 0.1, 92
    width, height = config.WIDTH * 0.8, config.HEIGHT - 172
    bar_size = (32, 9)
    half_width = width / 2

    # (local centerx, local top) within the old HealthContainer's rect,
    # translated to absolute screen positions below.
    local_positions = [
        (half_width + 4, height * 0.06),        # head
        (half_width * 0.63, height * 0.3),      # left arm
        (half_width * 0.63, height * 0.61),     # left leg
        (half_width * 1.38, height * 0.3 + 1),  # right arm
        (half_width * 1.38, height * 0.61 + 1), # right leg
        (half_width + 4, height * 0.72 + 14),   # full body
    ]

    for local_centerx, local_top in local_positions:
        image = render_progressbar(ProgressBarState(dimensions=bar_size, value=100, max_value=100, border_width=1))
        x = left + local_centerx - bar_size[0] / 2
        y = top + local_top
        esper.create_entity(Position(x, y), Renderable(image=image), Layer(5), Dirty(1), OwnedBy(NODE_KEY))
