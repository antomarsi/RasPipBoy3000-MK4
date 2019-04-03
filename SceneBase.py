class SceneBase:
    def __init__(self):
        self.next = self

    def process_input(self, events):
        print("["+self.__class__.__name__+"]Override this process event")

    def update(self, dt):
        print("["+self.__class__.__name__+"]Override this process event")

    def render(self, render):
        print("["+self.__class__.__name__+"]Override this process event")

    def switch_to_scene(self, next_scene):
        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)
