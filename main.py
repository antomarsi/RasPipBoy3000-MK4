from core import SceneManager
from scenes.intro import IntroScene

if __name__ == '__main__':
    SceneManager("intro", {"intro": IntroScene()}, title="RasPipBoy 3000 MK IV", show_fps=True)
