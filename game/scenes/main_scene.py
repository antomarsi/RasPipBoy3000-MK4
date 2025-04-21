
from core.scene_base import SceneBase
from scenes.loading_scene import LoadingScene

class MainScene(SceneBase):

    def __init__(self):
        super().__init__()
        self.add_entity("loading_scene", LoadingScene(), True)

