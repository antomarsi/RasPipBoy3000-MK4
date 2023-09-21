import pygame
import os
from rasp_pipboy.utils.config import ConfigSettings

class ResourceLoader:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ResourceLoader.__instance == None:
            ResourceLoader()
        return ResourceLoader.__instance

    def __init__(self):
        """ Virtually private constructor. """
        self._image_library = {}
        self._sound_library = {}
        self._font_library = {}
        self.assets_folder = ConfigSettings().assets_folder
        if ResourceLoader.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ResourceLoader.__instance = self

    def add_image(self, key, path):
        self._image_library[key] = pygame.image.load(os.path.join(self.assets_folder, path)).convert_alpha()

    def get_image(self, key):
        if key not in self._image_library.keys():
            return None
        return self._image_library[key].copy()

    def add_sound(self, key, path):
        if key not in self._sound_library.keys():
            sound = pygame.mixer.Sound(
                os.path.join(self.assets_folder, path))
            self._sound_library[key] = sound

    def add_font(self, key, path, size = 12):
        key = f"{key}_{size}"
        if key not in self._font_librart.keys():
            font = pygame.font.Font(os.path.join(ConfigSettings().assets_folder, 'fonts', path), size)
            self._font_library[key] = font

    def get_font(self, key, size):
        key = f"{key}_{size}"
        if key not in self._font_library.keys():
            return None
        return self._font_library[key]

    def get_sound(self, key):
        if key not in self._sound_library.keys():
            return None
        return self._sound_library[key]

    def play_sound(self, path):
        self.get_sound(path).play()

    def play_music(self, path, loops=-1):
        path = os.path.join(cfg.assets_folder, path.replace(
            '/', os.sep).replace('\\', os.sep))
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loops)
