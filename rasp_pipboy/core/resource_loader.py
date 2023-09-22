import pygame as pg
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
        self.sound_volume = 1.0

        self.music = {}
        self.target_music_volume = 1.0
        self.volume_increment = 0.01

        self.music_volume = 1.0
        self.next_music = None
        self.current_music = None

        if ResourceLoader.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ResourceLoader.__instance = self

    def add_image(self, key, path):
        self._image_library[key] = pg.image.load(os.path.join(self.assets_folder, path)).convert_alpha()

    def get_image(self, key):
        if key not in self._image_library.keys():
            return None
        return self._image_library[key].copy()

    def add_sound(self, key, path):
        if key not in self._sound_library.keys():
            sound = pg.mixer.Sound(
                os.path.join(self.assets_folder, path))
            self._sound_library[key] = sound
    
    def play_sound(self, key):
        self.get_sound(key).play()

    def get_sound(self, key):
        if key not in self._sound_library.keys():
            return None
        return self._sound_library[key]


    def add_font(self, key, path, size = 12):
        key = f"{key}_{size}"
        if key not in self._font_library.keys():
            font = pg.font.Font(os.path.join(ConfigSettings().assets_folder, 'fonts', path), size)
            self._font_library[key] = font

    def get_font(self, key, size) -> pg.font.Font:
        key = f"{key}_{size}"
        if key not in self._font_library.keys():
            return None
        return self._font_library[key]

    def play_music(self, music_name, loop=True):

        if music_name is self.current_music:
            return
        pg.mixer.music.load(self.music[music_name])
        self.current_music = music_name

        if loop:
            pg.mixer.music.play(-1)
        else:
            pg.mixer.music.play(0)

    def play_music_fade(self, music_name, duration):
        if music_name is self.current_music:
            return
        self.next_music = music_name
        self.fadeOut(duration)
    
    def set_music_volume(self, volume, duration=1):
        self.volume_increment = 1/duration
        self.target_music_volume = volume
    
    def fadeOut(self, duration=1000):
        pg.mixer.music.fadeout(duration)
        self.current_music = None
    
    def update(self):
        if self.music_volume < self.target_music_volume:
            self.music_volume = min(self.music_volume + self.volume_increment, self.target_music_volume)
            pg.mixer.music.set_volume(self.music_volume)
        if self.music_volume > self.target_music_volume:
            self.music_volume = min(self.music_volume + self.volume_increment, self.target_music_volume)
            pg.mixer.music.set_volume(self.music_volume)

        if self.next_music is not None:
            if not pg.mixer.music.get_busy():
                self.current_music = None
                self.music_volume = 0
                pg.mixer.music.set_volume(self.music_volume)
                self.play_music(self.next_music)
                self.next_music = None