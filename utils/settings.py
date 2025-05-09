import os
from typing import Tuple, Any, Optional, Union
from functools import cached_property
from pydantic import Field, computed_field
from pydantic.fields import FieldInfo
from utils.color import hex_to_rgb
from utils.logger import logger
import pygame as pg

from pydantic_settings import EnvSettingsSource, BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource


class MyCustomSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name in ['BG_COLOR', "TINT_COLOR", "DRAW_COLOR"] and value is not None:
            return hex_to_rgb(value)
        return value


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')
    WIDTH: int = 720
    HEIGHT: int = 540

    OUTPUT_WIDTH: Optional[int] = 720
    OUTPUT_HEIGHT: Optional[int] = 540
    RESCALE: bool = False

    FRAMERATE: int = 60

    SOUND_ENABLED: bool = Field(default=False, validation_alias="SOUND_ENABLED")
    DRAW_COLOR: Tuple[float, float, float] = Field(
        default=(0.0, 255.0, 0.0), validation_alias="DRAW_COLOR")
    TINT_COLOR: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0), validation_alias="TINT_COLOR")
    BG_COLOR: Tuple[int, int, int] = Field(
        default=(0, 0, 0), validation_alias="BG_COLOR")

    ASSETS_FOLDER: str


    GPIO_ACTIONS: dict = {
        4: "module_stat",  # GPIO 4
        14: "module_inv",  # GPIO 14
        15: "module_data",  # GPIO 15
        16: "module_map",  # GPIO ?
        19: "module_radio",  # GPIO ?
        17:	"knob_1",  # GPIO 17
        18: "knob_2",  # GPIO 18
        7: "knob_3",  # GPIO 7
        22: "knob_4",  # GPIO 22
        23: "knob_5",  # GPIO 27
        31: "dial_up", #GPIO 23
        27: "dial_down"  # GPIO 7
    }

    ACTIONS: dict = {
        pg.K_F1: "module_stat",
        pg.K_F2: "module_inv",
        pg.K_F3: "module_data",
        pg.K_F4: "module_map",
        pg.K_F5: "module_radio",
        pg.K_1:	"knob_1",
        pg.K_2: "knob_2",
        pg.K_3: "knob_3",
        pg.K_4: "knob_4",
        pg.K_5: "knob_5",
        pg.K_UP: "dial_up",
        pg.K_DOWN: "dial_down"
    }

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (MyCustomSource(settings_cls),)

    @computed_field
    @cached_property
    def GPIO_AVALIABLE(self) -> bool:
        try:
            import RPi.GPIO as GPIO  # type: ignore
            logger.info("✅ GPIO found")
            return True
        except:
            logger.info("❌ GPIO not found")

        return False

    @computed_field
    @cached_property
    def SIZE(self) -> Tuple[int, int]:
        return (self.WIDTH, self.HEIGHT)

    @computed_field
    @cached_property
    def OUTPUT_SIZE(self) -> Optional[Tuple[int, int]]:
        if not self.RESCALE or not self.OUTPUT_WIDTH or not self.OUTPUT_HEIGHT:
            return None
        return (self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT)

    ASSETS_FOLDER: str = os.path.abspath("./assets")
    DOWNLOAD_FOLDER: str = os.path.abspath("./download")

    DOWNLOAD_RADIO: bool = True
    USE_BLUR: bool = True
    USE_SCANLINE: bool = True
    SKIP_INTRO: bool = Field(default=False, validation_alias="SKIP_INTRO")
    RADIOS: dict = {
        "Wastland": "https://www.youtube.com/watch?v=5eAalHA1bAc",
    }

    MODULE_TEXTS: list[str] = ["STAT", "INV", "DATA", "MAP", "RADIO"]

    hide_top_menu: Union[bool, int] = False


config = ConfigSettings()
