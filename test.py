import pygame
import pygame_shaders


pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)

screen = pygame.display.set_mode((600, 600), pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE)  # Create an opengl renderable display.

display = pygame.Surface((600, 600))  # Create a new surface, this will be where you do all your pygame rendering
display.set_colorkey((0, 0, 0))  # Make all black on the display transparent

shader = pygame_shaders.Shader(
    size=(600, 600),
    display=(600, 600),
    pos=(0, 0),
    vertex_path="./shaders/vertex.txt",
    fragment_path="./shaders/fragment.txt",
    target_texture=display
)  # Load your shader!

while True:
    pygame_shaders.clear((0, 0, 0))  # Fill with the color you would like in the background
    display.fill((0, 0, 0))  # Fill with the color you set in the colorkey

    # Your pygame code here.

    pygame.draw.rect(
        display, (255, 255, 255), (20, 20, 20, 20)
    )  # Draw a red rectangle to the display at (20, 20)

    shader.render(display)
    pygame.display.flip()
    print("running")
