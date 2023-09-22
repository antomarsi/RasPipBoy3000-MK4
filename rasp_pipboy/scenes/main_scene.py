
from rasp_pipboy.core.scene_base import SceneBase
from rasp_pipboy.scenes.loading_scene import LoadingScene

class MainScene(SceneBase):

    def __init__(self):
        super().__init__("Main")
        self.add_entity("loading_scene", LoadingScene(), True)

