import esper
import pygame as pg
import pytweening

from core.components import Active, AnimationState, AutoScroll, Dirty, Layer, Position, Renderable, Tween


class TweenProcessor(esper.Processor):
    def process(self, dt):
        for ent, tween in esper.get_component(Tween):
            if not tween.playing:
                continue
            tween.elapsed += dt
            t = 1.0 if tween.duration <= 0 else min(tween.elapsed / tween.duration, 1.0)
            easing = tween.easing or pytweening.linear
            value = tween.start + (tween.end - tween.start) * easing(t)
            tween.apply(value)
            if t >= 1.0:
                tween.playing = False
                esper.remove_component(ent, Tween)
                if tween.on_complete:
                    tween.on_complete()


class AnimationProcessor(esper.Processor):
    def process(self, dt):
        for ent, (anim, renderable) in esper.get_components(AnimationState, Renderable):
            if not anim.playing or not anim.frames:
                continue
            anim.elapsed += dt
            advanced = False
            while anim.elapsed >= anim.duration_per_frame:
                anim.elapsed -= anim.duration_per_frame
                advanced = True
                if anim.current_frame >= len(anim.frames) - 1:
                    if anim.loop:
                        anim.current_frame = 0
                    else:
                        anim.playing = False
                        anim.finished = True
                        break
                else:
                    anim.current_frame += 1
            if advanced:
                renderable.image = anim.frames[anim.current_frame]
                dirty = esper.try_component(ent, Dirty)
                if dirty:
                    dirty.state = 1
                if anim.finished and anim.on_complete:
                    anim.on_complete()


class AutoScrollProcessor(esper.Processor):
    def process(self, dt):
        for ent, (pos, scroll) in esper.get_components(Position, AutoScroll):
            pos.y += scroll.speed * dt
            if pos.y >= scroll.max_y:
                pos.y = scroll.min_y
            dirty = esper.try_component(ent, Dirty)
            if dirty:
                dirty.state = 2


class RenderProcessor:
    """Composites every Active, visible (Position, Renderable, Layer) entity
    onto `screen`, in layer order, every frame.

    This is a full redraw of the ECS-owned layer each frame rather than a true
    per-rect dirty compositor: correctly handling overlap between
    independently-dirty layers needs the same dependency tracking
    pygame.sprite.LayeredDirty already does internally, which isn't worth
    re-implementing for a screen this size. `dirty_this_frame` instead tracks
    whether anything's *state* actually changed this frame (Dirty.state != 0)
    -- that's the signal PipBoy.run()'s battery-saving idle framerate cares
    about, which is a different question from "was anything blitted".

    Not registered as an esper.Processor (its process() takes no dt and must
    run during the render phase, not the update phase) -- invoked directly by
    Engine.render().
    """

    def __init__(self, screen, bg_color=(0, 0, 0)):
        self.screen = screen
        self.bg_color = bg_color
        self.dirty_this_frame = False

    def process(self):
        self.screen.fill(self.bg_color)
        entities = [
            (layer.order, ent, pos, renderable)
            for ent, (pos, renderable, layer) in esper.get_components(Position, Renderable, Layer)
            if esper.has_component(ent, Active) and renderable.visible and renderable.image is not None
        ]
        entities.sort(key=lambda e: e[0])

        self.dirty_this_frame = False
        rects = []
        for _, ent, pos, renderable in entities:
            # Additive blending, matching the app's CRT-glow look: every
            # sprite in the pre-ECS system blitted this way by default (see
            # the old core.engine.Entity.blendmode), which is what lets a
            # near-black, fully-opaque texture like the scanline/overlay
            # effect sit on top of content as a subtle brightness pattern
            # instead of occluding it outright.
            rects.append(self.screen.blit(renderable.image, (pos.x, pos.y), special_flags=pg.BLEND_RGBA_ADD))
            dirty = esper.try_component(ent, Dirty)
            if dirty and dirty.state != 0:
                self.dirty_this_frame = True
                if dirty.state == 1:
                    dirty.state = 0
        return rects
