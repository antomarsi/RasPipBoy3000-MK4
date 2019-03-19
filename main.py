import pyglet
import config
from system.component import Component
from entities.cursor import Cursor
from scenes.stats import StatsScene
from random import randint

window = pyglet.window.Window(height=config.window_height,
                              width=config.window_width)

scenes_objects = []
scenes_objects.append(StatsScene())
selected_index = 0


def draw():
    """
    Clears screen and then renders our list of ball objects
    :return:
    """
    window.clear()
    if isinstance(scenes_objects[selected_index], Component):
        scenes_objects[selected_index].draw_self()


def update(dt):
    """
    Updates our list of ball objects
    :param time:
    :return:
    """
    if isinstance(scenes_objects[selected_index], Component):
            scenes_objects[selected_index].update_self(dt)


@window.event
def on_mouse_press(x, y, button, modifiers):
    """
    On each mouse click, we create a new ball object
    print('x: {}, y: {}'.format(x, y))
    ball_objects.append(Cursor(x=x, y=y, speed=randint(3, 12)))
    """
    return


def main():
    """
    This is the main method. This contains an embedded method
    :return:
    """
    pyglet.font.add_file('assets/fonts/monofonto-kerned.ttf')
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

    @window.event
    def on_draw():
        draw()
    pyglet.clock.schedule_interval(update, 1/15.0)
    pyglet.app.run()


main()
