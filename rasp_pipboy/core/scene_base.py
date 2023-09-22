import pygame as pg

class SceneBase:

    def __init__(self, key):
        self.hided = False
        self.key = key
        self.entities = {}
        self.parent = None
    
    def set_parent(self, parent):
        self.parent = parent

    def initialize(self):
        print("["+self.__class__.__name__+"]Override this process event")

    def add_entity(self, key, entity, show=True):
        if key in self.entities.keys():
            raise Exception(f"Entity {key} already exists on scene{self.key}")
        self.entities[key] = entity
        self.entities[key].set_parent(parent=self)
        self.entities[key].hided = not show
    
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
        if key in self.entities.keys():
            raise Exception(f"Entity {key} already exists on scene{self.key}")
        self.entities[key].hided = True

    def show_entity(self, key):
        if key in self.entities.keys():
            raise Exception(f"Entity {key} already exists on scene{self.key}")
        self.entities[key].hided = False

    def terminate(self):
        pass