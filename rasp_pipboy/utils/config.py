import os
from typing import Tuple, Any, Type
from pydantic import Field
from pydantic.fields import FieldInfo
from .colors import hex_to_rgb
import pygame as pg

from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource, EnvSettingsSource

class MyCustomSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name in ['tint_color', 'bg_color'] and value is not None:
            return hex_to_rgb(value)
        return value


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', env_prefix='PIPBOY_')

    caption : str = "RasPipBoy-3000 Mk IV"
    width : int = 480
    height: int = 320
    framerate : int = 60

    use_sound : bool = Field(default=True, validation_alias="USE_SOUND")
    tint_color : Tuple[int, int, int]= Field(default=(0, 200, 0), validation_alias="TINT_COLOR")
    bg_color : Tuple[int, int, int]= Field(default=(0, 0, 0), validation_alias="BG_COLOR")

    assets_folder : str ()


    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (MyCustomSource(settings_cls),)

    assets_folder :str = os.path.abspath("./assets")
    download_folder :str = os.path.abspath("./download")

    download_radio : bool = True
    use_blur : bool = True
    use_scanline : bool = True
    skip_intro : bool = Field(default=False, validation_alias="SKIP_INTRO")
    radios : dict = {
        "Wastland": "https://www.youtube.com/watch?v=5eAalHA1bAc",
    }

