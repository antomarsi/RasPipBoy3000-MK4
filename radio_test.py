import spotipy
from dotenv import load_dotenv
import spotipy.util as util
import sys
import pyaudio
import numpy as np
import pygame
import time

load_dotenv()

redirect_uri = "http://localhost:8888/callback"
scope = "user-modify-playback-state"

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username, scope, redirect_uri=redirect_uri)

if not token:
    print("Can't get token for", username)
    sys.exit()

sp = spotipy.client.Spotify(auth=token)
# sp.next_track()

CHUNK = 128
RATE = 44100


def sound(stream):
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)


def main():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    clock = pygame.time.Clock()
    FPS = 60
    # graphic interface dimensions
    width = 420
    height = 360
    center = [width/2, height/2]

    # scale the amplitude to 1/4th of the frame height and translate it to height/2(central line)
    max_amplitude = 2**16/2
    min_amplitude = -2**16/2
    # for i in range(len(amplitude)):
    #   amplitude[i] = float(amplitude[i])/max_amplitude*height/4 + height/2
    # amplitude = [int(height/2)]*width + list(amplitude)

    # initiate graphic interface and play audio piece
    pygame.init()
    font = pygame.font.Font(None, 30)
    screen = pygame.display.set_mode([width, height])
    now = time.time()

    # visualizer animation starts here
    done = False
    multiplier = 1.5
    while not done:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        x_unit = width / len(data)
        screen.fill([0, 0, 0])
        # print(max_amplitude)
        # print(data)
        # the amplitude graph is being translated from both left and right creating a mirror effect
        points = []
        for index, freq in enumerate(data):
            value = ((freq - min_amplitude) * 100) / \
                (max_amplitude - min_amplitude)
            #print([int(index*x_unit), int(height*(value/100))])
            points.append([int(index*x_unit), int(height*(value/100)*multiplier)])
        pygame.draw.lines(screen, [0, 255, 0], False, points, 1)
        # for x in enumerate(amplitude[i+1:i+1+width][::5]):
        #   pygame.draw.line(screen, [0, 255, 0], [prev_x*5, prev_y], [x*5, y], 1)
        #   pygame.draw.line(screen, [0, 255, 0], [
        #                    (prev_x*5-width/2)*-1+width/2, prev_y], [(x*5-width/2)*-1+width/2, y], 1)
        #   prev_x,	prev_y=x, y

        # time delay to control frame refresh rate
        fps = font.render(str(int(clock.get_fps())), True, pygame.Color('white'))
        screen.blit(fps, (50, 50))
        pygame.display.flip()
        clock.tick(FPS)
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
    main()
