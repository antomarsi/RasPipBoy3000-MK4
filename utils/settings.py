import os
from typing import Tuple, Optional
from functools import cached_property
from pydantic import Field, computed_field
from utils.logger import logger
import pygame as pg

from pydantic_settings import DotEnvSettingsSource, BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')
    WIDTH: int = 720
    HEIGHT: int = 540

    OUTPUT_WIDTH: Optional[int] = 720
    OUTPUT_HEIGHT: Optional[int] = 540
    RESCALE: bool = False

    FRAMERATE: int = 60
    IDLE_FRAMERATE: int = 15
    STARTUP_MODULE: str = "stat"

    # Visual theme (draw/tint/background colors) lives in the save-data store
    # (game/data/store.py's ThemeSettings), not here — it's user-changeable
    # state, not restart-only deployment config.

    GPIO_ACTIONS: dict = {
        4: "module_stat",
        14: "module_inv",
        15: "module_data",
        16: "module_map",
        19: "module_radio",
        17:	"knob_1",
        18: "knob_2",
        7: "knob_3",
        22: "knob_4",
        23: "knob_5",
        24: "dial_up",
        27: "dial_down"
    }

    ACTIONS: dict = {
        pg.K_1: "module_stat",
        pg.K_2: "module_inv",
        pg.K_3: "module_data",
        pg.K_4: "module_map",
        pg.K_5: "module_radio",
        pg.K_q: "submodule_prev",
        pg.K_e: "submodule_next",
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
        return (DotEnvSettingsSource(settings_cls),)

    @computed_field
    @cached_property
    def GPIO_AVAILABLE(self) -> bool:
        try:
            import gpiozero  # type: ignore
            logger.info("✅ GPIO found")
            return True
        except:
            logger.info("❌ GPIO not found")

        return False

    @computed_field
    @cached_property
    def SOUND_ENABLED(self) -> bool:
        try:
            pg.mixer.init(44100, -16, 2, 2048)
            return True
        except Exception:
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
    SAVE_FILE: str = os.path.abspath("./save/state.json")

    USE_BLUR: bool = True
    USE_SCANLINE: bool = True
    HUM_ENABLED: bool = True
    SKIP_INTRO: bool = Field(default=False, validation_alias="SKIP_INTRO")
    RADIOS: dict = {
        "Wastland": "https://www.youtube.com/watch?v=5eAalHA1bAc",
    }


config = ConfigSettings()
