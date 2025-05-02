import ffmpeg
import pyaudio
import pygame
import numpy as np
import threading

# --- Config ---
STREAM_URL = "https://f111.fabricahost.com.br/jpblumenau?f=1746140476N01JT71ACTEB3J3RXGRKH49SYMP&tid=01JT71ACTEH1WNDNJ4NWTFEX8"
CHUNK = 1024
RATE = 44100
CHANNELS = 1

filters = {
    "clean": None,
    "radio": 'highpass=f=300, lowpass=f=3400, compand',
    "old_radio": "highpass=f=300, lowpass=f=3400, compand, volume=2, aecho=0.8:0.9:1000:0.3, acrusher=bits=8:mode=log",
    "fallout": "highpass=f=300, lowpass=f=3400, compand=attacks=0:decays=0:points=-90/-900|-60/-60|0/0, acrusher=bits=6:mode=log, aecho=0.8:0.9:1000:0.3, volume=1.5"
}

key_filter = {pygame.K_1: "clean", pygame.K_2: "radio", pygame.K_3: "old_radio", pygame.K_4: "fallout"}

current_filter = "clean"
ffmpeg_process = None
running = True
waveform_data = np.zeros(CHUNK)

# PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                output=True)

ffmpeg_process = (
        ffmpeg
        .input(STREAM_URL)
        .output('pipe:', format='s16le', acodec='pcm_s16le', ac=CHANNELS, ar=RATE)
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )


def start_ffmpeg(filter_name):
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.kill()
    af = filters[filter_name]
    if af:
        ffmpeg_process = (
            ffmpeg
            .input(STREAM_URL)
            .output('pipe:', format='s16le', acodec='pcm_s16le', ac=CHANNELS, ar=RATE, af=af)
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )
    else:
        ffmpeg_process = (
            ffmpeg
            .input(STREAM_URL)
            .output('pipe:', format='s16le', acodec='pcm_s16le', ac=CHANNELS, ar=RATE)
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

def audio_loop():
    global waveform_data
    while running:
        raw_audio = ffmpeg_process.stdout.read(CHUNK * 2)
        if not raw_audio:
            continue
        stream.write(raw_audio)
        samples = np.frombuffer(raw_audio, dtype=np.int16)
        waveform_data = samples

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 300))
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

# Start audio thread
start_ffmpeg(current_filter)
thread = threading.Thread(target=audio_loop, daemon=True)
thread.start()

# Main loop
while running:
    screen.fill((0, 0, 0))

    text = font.render(f"Effect: {current_filter}", True, (0, 255, 0))
    screen.blit(text, (10, 10))

    # Draw waveform
    mid_y = screen.get_height() // 2
    samples = waveform_data[::2]
    normalized = samples / 32768.0
    points = []
    for i, sample in enumerate(normalized):
        x = int(i * screen.get_width() / len(normalized))
        y = int(mid_y + sample * mid_y)
        points.append((x, y))
    if len(points) > 1:
        pygame.draw.lines(screen, (0, 255, 0), False, points, 2)

    pygame.display.flip()
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key in key_filter.keys():
                current_filter = key_filter[event.key]
                start_ffmpeg(current_filter)
# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
ffmpeg_process.kill()
pygame.quit()
