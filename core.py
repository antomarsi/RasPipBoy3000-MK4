import pyglet


class SceneManager(object):

    def on_step(self, dt):
        if not self.running:
            self.window.close()
            pyglet.app.exit()
        else:
            self.scenes[self.current].on_step(self, dt)

    def __init__(self, start, scenes, x=640, y=360, title='Untitled', fps=30, show_fps=False):
        self.running = True
        self.current = start
        self.scenes = scenes
        self.window = pyglet.window.Window(x, y, title)
        pyglet.clock.schedule_interval(self.on_step, 1.0/fps)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,
                              pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        self.show_fps = show_fps
        pyglet.clock.set_fps_limit(fps)
        self.fps_display = pyglet.window.FPSDisplay(self.window)

        @self.window.event
        def on_activate():
            self.scenes[self.current].on_activate(self)

        @self.window.event
        def on_close():
            self.scenes[self.current].on_close(self)

        @self.window.event
        def on_context_lost():
            self.scenes[self.current].on_context_lost(self)

        @self.window.event
        def on_context_state_lost():
            self.scenes[self.current].on_context_state_lost(self)

        @self.window.event
        def on_deactivate():
            self.scenes[self.current].on_deactivate(self)

        @self.window.event
        def on_draw():
            self.scenes[self.current].on_draw(self)
            if self.show_fps:
                self.fps_display.draw()

        @self.window.event
        def on_expose():
            self.scenes[self.current].on_expose(self)

        @self.window.event
        def on_hide():
            self.scenes[self.current].on_hide(self)

        @self.window.event
        def on_key_press(symbol, modifiers):
            self.scenes[self.current].on_key_press(self, symbol, modifiers)

        @self.window.event
        def on_key_release(symbol, modifiers):
            self.scenes[self.current].on_key_release(self, symbol, modifiers)

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            self.scenes[self.current].on_mouse_drag(
                self, x, y, dx, dy, buttons, modifiers)

        @self.window.event
        def on_mouse_enter(x, y):
            self.scenes[self.current].on_mouse_enter(self, x, y)

        @self.window.event
        def on_mouse_leave(x, y):
            self.scenes[self.current].on_mouse_leave(self, x, y)

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            self.scenes[self.current].on_mouse_motion(self, x, y, dx, dy)

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.scenes[self.current].on_mouse_press(
                self, x, y, button, modifiers)

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.scenes[self.current].on_mouse_release(
                self, x, y, button, modifiers)

        @self.window.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            self.scenes[self.current].on_mouse_scroll(
                self, x, y, scroll_x, scroll_y)

        @self.window.event
        def on_move(x, y):
            self.scenes[self.current].on_move(self, x, y)

        @self.window.event
        def on_resize(width, height):
            self.scenes[self.current].on_resize(self, width, height)

        @self.window.event
        def on_show():
            self.scenes[self.current].on_show(self)

        @self.window.event
        def on_text(text):
            self.scenes[self.current].on_text(self, text)

        @self.window.event
        def on_text_motion(motion):
            self.scenes[self.current].on_text_motion(self, motion)

        @self.window.event
        def on_text_motion_select(motion):
            self.scenes[self.current].on_text_motion_select(self, motion)

        pyglet.app.run()


class Scene(object):
    """Scene template."""

    def on_step(self, app, dt):
        pass

    def on_activate(self, app):
        pass

    def on_close(self, app):
        pass

    def on_context_lost(self, app):
        pass

    def on_context_state_lost(self, app):
        pass

    def on_deactivate(self, app):
        pass

    def on_draw(self, app):
        pass

    def on_expose(self, app):
        pass

    def on_hide(self, app):
        pass

    def on_key_press(self, app, symbol, modifiers):
        pass

    def on_key_release(self, app, symbol, modifiers):
        pass

    def on_mouse_drag(self, app, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_enter(self, app, x, y):
        pass

    def on_mouse_leave(self, app, x, y):
        pass

    def on_mouse_motion(self, app, x, y, dx, dy):
        pass

    def on_mouse_press(self, app, x, y, button, modifiers):
        pass

    def on_mouse_release(self, app, x, y, button, modifiers):
        pass

    def on_mouse_scroll(self, app, x, y, scroll_x, scroll_y):
        pass

    def on_move(self, app, x, y):
        pass

    def on_resize(self, app, width, height):
        pass

    def on_show(self, app):
        pass

    def on_text(self, app, text):
        pass

    def on_text_motion(self, app, motion):
        pass

    def on_text_motion_select(self, app, motion):
        pass
