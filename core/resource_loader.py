import pygame as pg
from os.path import join
from utils.config import config as pipconfig


class ResourceLoader:
    _asset_folder = pipconfig.ASSETS_FOLDER

    """ Resource library """
    _image_library: dict[str, pg.Surface] = {}
    _sound_library: dict[str, pg.mixer.Sound] = {}
    _font_library: dict[str, pg.font.Font] = {}

    def __new__(cls):
        raise NotImplementedError("This class cannot be instantiated.")

    @staticmethod
    def add_image(key: str, path: str) -> pg.Surface:
        if key not in ResourceLoader._image_library.keys():
            filepath = join(ResourceLoader._asset_folder, path)
            ResourceLoader._image_library[key] = pg.image.load(
                filepath).convert_alpha()
        return ResourceLoader._image_library[key]

    @staticmethod
    def get_image(key: str) -> pg.Surface:
        if key not in ResourceLoader._image_library.keys():
            raise Exception(
                f"Image \"{key}\" not loaded.")
        return ResourceLoader._image_library[key]

    @staticmethod
    def remove_image(key: str):
        if key in ResourceLoader._image_library.keys():
            ResourceLoader._image_library.pop(key)

    @staticmethod
    def add_sound(key: str, path: str) -> pg.mixer.Sound:
        if key not in ResourceLoader._sound_library.keys():
            filepath = join(ResourceLoader._asset_folder, path)
            ResourceLoader._sound_library[key] = pg.mixer.Sound(filepath)
        return ResourceLoader._sound_library[key]

    @staticmethod
    def get_sound(key: str) -> pg.mixer.Sound:
        if key not in ResourceLoader._sound_library.keys():
            raise Exception(
                f"Sound \"{key}\" not loaded.")
        return ResourceLoader._sound_library[key]

    @staticmethod
    def remove_sound(key: str):
        if key in ResourceLoader._sound_library.keys():
            ResourceLoader._sound_library.pop(key)

    @staticmethod
    def add_font(key: str, path: str, size: int):
        key_size = f"{key}_{size}"
        if key_size not in ResourceLoader._font_library.keys():
            filename = join(ResourceLoader._asset_folder, path)
            ResourceLoader._font_library[key_size] = pg.font.Font(filename, size)
        return ResourceLoader._font_library[key_size]

    @staticmethod
    def get_font(key, size) -> pg.font.Font:
        key_size = f"{key}_{size}"
        if key_size not in ResourceLoader._font_library.keys():
            raise Exception(f"Font {key} of size {size} not loaded.")
        return ResourceLoader._font_library[key_size]
