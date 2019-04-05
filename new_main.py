import struct
import pygame as pg
import moderngl
from pygame.locals import *
import config as cfg
import os
from scenes.intro import IntroScene
from scanline_gradient import ScanLineGradient


class App(object):
    """
    Class responsible for program control flow.
    """
    def __init__(self, fps):
        self.screen = pg.Surface(pg.display.get_surface().get_size()).convert((16711680, 65280, 255, 0), 0)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = fps
        self.done = False
        self.keys = pg.key.get_pressed()
        self.ctx = moderngl.create_context()
        self.diffuse_texture = self.ctx.texture(self.screen.get_size(), 3, pg.image.tostring(self.screen, "RGB", 1))
        self.program = self.ctx.program(
        vertex_shader='''
            #version 140
            in vec2 vert;
            in vec2 in_text;
            out vec2 v_text;
            void main() {
                gl_Position = vec4(vert, 0.0, 1.0);
                v_text = in_text;
            }
        ''', fragment_shader='''
            #version 140
            uniform sampler2D t0;

            uniform vec2 blur_size = '''+ ("vec2(.1, .1)" if cfg.use_blur else  "vec2(0, 0)" )+''';

            out vec4 color;
            in vec2 v_text;
            void main() {
                vec4 temp = vec4(texture(t0, v_text).rgb, 1.0);

                ivec2 size = textureSize(t0, 0);

                float uv_x = v_text.x * size.x;
                float uv_y = v_text.y * size.y;

                vec4 sum = vec4(0.0);

                for (int n = 0; n < 9; ++n) {
                        uv_y = (v_text.y * size.y) + (blur_size.y * float(n - 4.5));
                        vec4 h_sum = vec4(0.0);
                        h_sum += texelFetch(t0, ivec2(uv_x - (4.0 * blur_size.x), uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x - (3.0 * blur_size.x), uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x - (2.0 * blur_size.x), uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x - blur_size.x, uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x, uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x + blur_size.x, uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x + (2.0 * blur_size.x), uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x + (3.0 * blur_size.x), uv_y), 0);
                        h_sum += texelFetch(t0, ivec2(uv_x + (4.0 * blur_size.x), uv_y), 0);
                        sum += h_sum / 9.0;
                    }

                color = sum / 9.0;
                ''' + ("color = color * (mod(v_text.y, (1.0/320.0)*2.0) * 2.0/(1.0/320.0));" if cfg.use_scanline else "") + '''
            }
        ''',
    )
        texture_coordinates = [0, 0,  1, 0,
                               0, 1,  1, 1]

        world_coordinates = [-1, -1,  1, -1,
                             -1,  1,  1,  1]

        render_indices = [0, 1, 2,
                          1, 2, 3]

        self.active_scene = IntroScene()

        self.vbo = self.ctx.buffer(struct.pack('8f', *world_coordinates))
        self.uv = self.ctx.buffer(struct.pack('8f', *texture_coordinates))
        self.ibo=self.ctx.buffer(struct.pack('6I', *render_indices))

        vao_content = [
            (self.vbo, '2f', 'vert'),
            (self.uv, '2f', 'in_text')
        ]

        self.vao = self.ctx.vertex_array(self.program, vao_content, self.ibo)
        self.font = pg.font.Font(None, 30)
        self.show_fps = False
        self.sprite_list = pg.sprite.LayeredDirty((ScanLineGradient()))

    def event_loop(self):
        pressed_keys = pg.key.get_pressed()
        filtered_events = []
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F3:
                    self.show_fps = not self.show_fps
            if self.done == True and self.active_scene != None:
                self.active_scene.terminate()
            else:
                filtered_events.append(event)

        if self.active_scene != None:
            self.active_scene.process_input(filtered_events, pressed_keys)

    def update(self, dt):
        """
        Update must acccept and pass dt to all elements that need to update.
        """
        if self.active_scene != None:
            self.active_scene.update(dt)
        self.sprite_list.update(dt)

    def render(self):
        """
        Render all needed elements and update the display.
        """
        self.screen.fill(cfg.background_color)

        if self.active_scene != None:
            self.active_scene.render(self.screen)
        self.sprite_list.draw(self.screen)

        if self.show_fps:
            self.screen.blit(self.font.render(str(int(self.clock.get_fps())), True, pg.Color('white')), (10, 10))

        texture_data = pg.transform.flip(self.screen, False, True).get_view('1')
        self.diffuse_texture.write(texture_data)
        self.ctx.clear(14/255,40/255,66/255)
        self.diffuse_texture.use()

        self.vao.render()
        pg.display.flip()

    def main_loop(self):
        """
        We now use the return value of the call to self.clock.tick to
        get the time delta between frames.
        """
        dt = 0
        self.clock.tick(self.fps)
        while not self.done:
            self.event_loop()
            self.update(dt)
            self.render()
            if self.active_scene != None:
                self.active_scene = self.active_scene.next


            dt = self.clock.tick(self.fps)/1000.0

def main():
    """
    Initialize; create an App; and start the main loop.
    """
    mode_flags = DOUBLEBUF | OPENGL
    if cfg.fullscreen:
        mode_flags |= pg.FULLSCREEN
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    framerate = cfg.DEFAULT_FRAMERATE
    pg.init()
    pg.display.set_caption(cfg.DEFAULT_CAPTION)
    pg.display.set_mode((cfg.width, cfg.height), mode_flags)
    App(framerate).main_loop()
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
