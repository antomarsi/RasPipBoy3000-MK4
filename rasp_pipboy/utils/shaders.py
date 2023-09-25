import moderngl
import pygame as pg
import struct


class Shader:
    def __init__(self, target_surface, use_scanline = True):
        self.ctx = moderngl.create_context()

        self.target_surface = target_surface

        self.diffuse_texture = self.ctx.texture(
            self.target_surface.get_size(), 3, pg.image.tostring(self.target_surface, "RGB", 1)
        )

        self.program = self.ctx.program(
            vertex_shader="""
            #version 300 es
            in vec2 vert;
            in vec2 in_text;
            out vec2 v_text;
            void main() {
                gl_Position = vec4(vert, 0.0, 1.0);
                v_text = in_text;
            }
        """,
            fragment_shader="""
            #version 300 es
            precision mediump float;
            uniform sampler2D Texture;

            out vec4 color;
            in vec2 v_text;
            void main() {
              vec2 center = vec2(0.5, 0.5);
              vec2 off_center = v_text - center;
              vec2 off_center2 = pow(abs(off_center), vec2(3.5, 3.5));

              vec2 v_text2 = center+off_center*(1.0+off_center2.yx*0.2);

              if (v_text2.x > 1.0 || v_text2.x < 0.0 ||
                  v_text2.y > 1.0 || v_text2.y < 0.0){
                 color=vec4(0.0, 0.0, 0.0, 1.0);
              } else {
                 color = vec4(texture(Texture, v_text2).rgb, 1.0);
                 float fv = fract(v_text2.y * float(textureSize(Texture,0).y));
                 fv=min(1.0, 0.8+0.5+min(fv, 1.0-fv));
                 color.rgb*=fv;
              }
              """
            + (
                "color = color * (mod(v_text.y, (1.0/320.0)*2.0) * 2.0/(1.0/320.0));"
                if use_scanline
                else ""
            )
            + """
            }""",
        )

        texture_coordinates = [0, 0, 1, 0, 0, 1, 1, 1]

        world_coordinates = [-1, -1, 1, -1, -1, 1, 1, 1]

        render_indices = [0, 1, 2, 1, 2, 3]

        vbo = self.ctx.buffer(struct.pack("8f", *world_coordinates))
        uv = self.ctx.buffer(struct.pack("8f", *texture_coordinates))
        ibo = self.ctx.buffer(struct.pack("6I", *render_indices))

        vao_content = [(vbo, "2f", "vert"), (uv, "2f", "in_text")]

        self.vao = self.ctx.vertex_array(self.program, vao_content, ibo)

    def render(self, surface):
        texture_data = pg.transform.flip(surface, False, True).get_view("1")
        self.diffuse_texture.write(texture_data)
        self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
        self.diffuse_texture.use()

        self.vao.render()
