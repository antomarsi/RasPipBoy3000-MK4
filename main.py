import pyglet
import config
from system.component import Component
from entities.cursor import Cursor
from random import randint

window = pyglet.window.Window(height=config.window_height,
                              width=config.window_width)

scenes_objects = []
selected_scene = []


def draw():
    """
    Clears screen and then renders our list of ball objects
    :return:
    """
    window.clear()
    if isinstance(selected_scene, Component):
        selected_scene.draw_self()


def update(time):
    """
    Updates our list of ball objects
    :param time:
    :return:
    """
    if isinstance(selected_scene, Component):
        selected_scene.update_self()


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
    @window.event
    def on_draw():
        draw()
    pyglet.clock.schedule_interval(update, 1/15.0)
    pyglet.app.run()


main()
