import pygame as pg

class SceneBase:

    def __init__(self):
        self.hided = False
        self.entities = {}
        self.parent = None
    
    def set_parent(self, parent):
        self.parent = parent
    
    def  on_hide(self):
        pass

    def on_show(self):
        pass

    def initialize(self):
        print("["+self.__class__.__name__+"]Override this process event")

    def add_entity(self, key, entity, show=True):
        if key in self.entities.keys():
            raise Exception(f"Entity {key} already exists on scene {self.key}")
        self.entities[key] = entity
        self.entities[key].key = key
        self.entities[key].set_parent(parent=self)
        self.entities[key].hided = not show

    def get_entity(self, key):
        if key not in self.entities.keys():
            raise Exception(f"Entity {key} not exists on scene {self.key}")
        return self.entities[key]
    
    def remove_entity(self, key):
        self.entities[key].terminate()
        self.entities.pop(key)

    def process_input(self, events, keys):
        for entity in self.entities.values():
            if not entity.hided:
                entity.process_input(events, keys)

    def update(self, dt: float):
        for entity in self.entities.values():
            if not entity.hided:
                entity.update(dt)

    def render(self, render: pg.Surface):
        for entity in self.entities.values():
            if not entity.hided:
                entity.render(render)
    
    def hide_entity(self, key):
        if key not in self.entities.keys():
            raise Exception(f"Entity {key} doesn't exists on scene{self.key}")
        self.entities[key].hided = True
        self.entities[key].on_hide()

    def show_entity(self, key):
        if key not in self.entities.keys():
            raise Exception(f"Entity {key} doesn't exists on scene{self.key}")
        self.entities[key].hided = False
        self.entities[key].on_show()

    def terminate(self):
        pass