import pygame as pg
from typing import List, Union

from core.engine import Entity


def scale_surface_keep_aspect(surface, max_width=None, max_height=None):
    if isinstance(surface, pg.Surface):
        orig_width, orig_height = surface.get_size()
    else:
        orig_width, orig_height = surface.rect.size

    if max_width is None and max_height is None:
        return surface  # No scaling needed

    # Calculate aspect ratio
    aspect_ratio = orig_width / orig_height

    if max_width and max_height:
        # Fit within both constraints
        scale_w = max_width
        scale_h = int(scale_w / aspect_ratio)
        if scale_h > max_height:
            scale_h = max_height
            scale_w = int(scale_h * aspect_ratio)
    elif max_width:
        scale_w = max_width
        scale_h = int(scale_w / aspect_ratio)
    elif max_height:
        scale_h = max_height
        scale_w = int(scale_h * aspect_ratio)

    return pg.transform.smoothscale(surface, (scale_w, scale_h))


def layout_flex_row(surfaces: List[Union[pg.Surface, Entity]], container_rect: pg.Rect, spacing=0):
    final_surface = pg.Surface(container_rect.size, pg.SRCALPHA)
    total_fixed_width = 0
    flex_surfaces_indexes = []

    for index, fs in enumerate(surfaces):
        if hasattr(fs, "flex"):
            flex_surfaces_indexes.append(index)
        else:
            total_fixed_width += fs.get_width()

    total_spacing = spacing * (len(surfaces) - 1)
    remaining_width = container_rect.width - total_fixed_width - total_spacing
    flex_count = len(flex_surfaces_indexes)

    if flex_count > 0:
        flex_width = max(0, remaining_width // flex_count)
        for index, fs in enumerate(surfaces):
            if index in flex_surfaces_indexes:
                if isinstance(fs, Entity) and hasattr(fs, "on_flex"):
                    fs.on_flex((flex_width, container_rect.height))
                else:
                    fs = scale_surface_keep_aspect(
                        fs,
                        flex_width, container_rect.height
                    )

    x = final_surface.get_rect().left
    for fs in surfaces:
        y = container_rect.top + \
            (container_rect.height - fs.get_height()) // 2
        final_surface.blit(fs, (x, y))
        x += fs.get_width() + spacing

    return final_surface

def layout_flex_row_sizes(surfaces: List[pg.Surface], container_rect: pg.Rect, spacing=0):
    total_fixed_width = 0
    flex_surfaces_indexes = []

    for index, fs in enumerate(surfaces):
        if hasattr(fs, "flex"):
            flex_surfaces_indexes.append(index)
        else:
            total_fixed_width += fs.get_width()

    total_spacing = spacing * (len(surfaces) - 1)
    remaining_width = container_rect.width - total_fixed_width - total_spacing
    flex_count = len(flex_surfaces_indexes)

    if flex_count > 0:
        flex_width = max(0, remaining_width // flex_count)
        for index, fs in enumerate(surfaces):
            if index in flex_surfaces_indexes:
                fs = scale_surface_keep_aspect(
                    fs,
                    flex_width, container_rect.height
                )
    sizes = []
    for fs in surfaces:
        sizes.append(fs.get_size())

    return sizes
