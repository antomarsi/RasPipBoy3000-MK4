class SceneBase:

    def __init__(self, key):
        self.key = key
        self.next = self
        self.entities = []

    def add_entities(self, key, entity):
        if key in self.entities.keys():
            raise Exception(f"Entity {key} already exists on scene{self.key}")
        self.entities[key] = entity
        self.entities[key]

    def process_input(self, events, keys):
        print("["+self.__class__.__name__+"]Override this process event")

    def update(self, dt):
        for entity in self.entities:
            entity.update(dt)

    def render(self, render):
        for entity in self.entities:
            entity.render(render)

    def switch_to_scene(self, next_scene):
        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)
