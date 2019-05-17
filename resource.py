import pygame
import os
import config as cfg


class Resource:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Resource.__instance == None:
            Resource()
        return Resource.__instance

    def __init__(self):
        """ Virtually private constructor. """
        self._image_library = {}
        self._sound_library = {}
        if Resource.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Resource.__instance = self

    def get_image(self, path):
        image = self._image_library.get(path)
        if image == None:
            abs_path = path.replace('/', os.sep).replace('\\', os.sep)
            image = pygame.image.load(
                os.path.join(cfg.assets_folder, abs_path))
            self._image_library[path] = image
        return image

    def get_sound(self, path):
        sound = self._sound_library.get(path)
        if sound == None:
            abs_path = path.replace('/', os.sep).replace('\\', os.sep)
            sound = pygame.mixer.Sound(
                os.path.join(cfg.assets_folder, abs_path))
            self._sound_library[path] = sound
        return sound

    def play_sound(self, path):
        self.get_sound(path).play()
