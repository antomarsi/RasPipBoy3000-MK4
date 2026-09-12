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
        pg.K_DOWN: "dial_down",
        # MAP-only today (ignored elsewhere -- registry.handle_action() has
        # no branch for map_filter). Keyboard-only stand-in for now; real
        # hardware controls (GPIO) still to be worked out for the map screen.
        # W/A/S/D are NOT mapped here -- MAP's cursor needs smooth,
        # continuous movement (held-key polling via pg.key.get_pressed()
        # every frame), which this discrete one-shot-per-keydown action
        # system can't express. See game/modules/map/__init__.py's
        # _CursorMoveProcessor.
        pg.K_f: "map_filter",
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
    # Each station is a local file (looped from assets/sounds/radio/, `path`
    # relative to that folder), a YouTube URL (downloaded once via yt-dlp
    # into RADIO_CACHE_DIR on first tune-in, then played from that local
    # copy forever after -- never a live stream, so a parked prop with
    # spotty connectivity still plays fine once fetched), or a direct
    # internet radio stream URL (`source: "stream"`, played live, never
    # cached -- see RADIO_ONLINE_STATION_COUNT below for stations found this
    # way automatically). `source: "tuner"` is a stub for real FM/AM
    # hardware, gated by LOCAL_RADIO_AVAILABLE -- not wired to any actual
    # receiver yet, since that's real hardware this project doesn't have
    # specifics for.
    #
    # `profile` (optional, per station) picks a distortion profile from
    # assets/data/radio_profiles.json -- defaults to "clean" (no distortion)
    # when omitted.
    RADIOS: dict = {
        "Wasteland Radio": {
            "source": "youtube", "url": "https://www.youtube.com/watch?v=5eAalHA1bAc",
            "profile": "fallout_broadcast",
        },
        "Local Mixtape": {"source": "local", "path": "mixtape.mp3"},
    }
    RADIO_CACHE_DIR: str = os.path.abspath("./save/radio_cache")
    LOCAL_RADIO_AVAILABLE: bool = False

    # How many currently-online stations (checked against the free,
    # community-run radio-browser.info directory -- no API key, filtered to
    # verified-working ones) get appended to the station list automatically.
    # 0 disables the online check entirely.
    RADIO_ONLINE_STATION_COUNT: int = 8
    RADIO_DIRECTORY_CACHE_MAX_AGE_S: float = 21600.0  # 6h -- the directory doesn't change fast

    GPS_SERIAL_PORT: str = "/dev/serial0"
    GPS_BAUDRATE: int = 9600
    GPS_POLL_INTERVAL_S: float = 2.0
    IP_GEO_URL: str = "http://ip-api.com/json/"
    # Fallback radii, used only before the first successful reverse-geocode
    # (or forever, in the degraded no-geocode offline case) -- once a city is
    # resolved, LOCAL's radius comes from that city's own bounding box
    # instead (see game/modules/map/geocode.py).
    MAP_LOCAL_RADIUS_M: float = 300.0
    MAP_WORLD_RADIUS_M: float = 3000.0
    MAP_CITY_RADIUS_MIN_M: float = 1000.0
    MAP_CITY_RADIUS_MAX_M: float = 15000.0
    MAP_CITY_RADIUS_DEFAULT_M: float = 5000.0
    MAP_REFRESH_INTERVAL_S: float = 120.0
    MAP_CACHE_DIR: str = os.path.abspath("./save/map_cache")
    MAP_CACHE_MAX_AGE_S: float = 86400.0

    @computed_field
    @cached_property
    def GPS_AVAILABLE(self) -> bool:
        try:
            import serial  # type: ignore
            import pynmea2  # type: ignore
            return True
        except ImportError:
            return False


config = ConfigSettings()
