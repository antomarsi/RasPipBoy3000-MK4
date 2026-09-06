from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from game.data.player import PlayerStatus
from utils.color import hex_to_rgb
from utils.logger import logger
from utils.settings import config

INVENTORY_CATEGORIES = ("weapons", "apparel", "aid", "misc", "junk", "mods", "ammo")


class ThemeSettings(BaseModel):
    draw_color: str = "00c800"
    tint_color: str = "00c800"
    bg_color: str = "000000"


class InventoryItem(BaseModel):
    baseid: str
    qtd: int = 1
    fav: bool = False
    eqp: bool = False


class SaveData(BaseModel):
    theme: ThemeSettings = Field(default_factory=ThemeSettings)
    player: PlayerStatus = Field(default_factory=PlayerStatus)
    inventory: dict[str, list[InventoryItem]] = Field(
        default_factory=lambda: {category: [] for category in INVENTORY_CATEGORIES})
    perks: list[dict] = Field(default_factory=list)
    quests: list[dict] = Field(default_factory=list)
    workshops: list[dict] = Field(default_factory=list)
    location: Optional[str] = None


def save_save(data: SaveData, path: Optional[str] = None) -> None:
    file_path = Path(path or config.SAVE_FILE)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(data.model_dump_json(indent=2), encoding="utf-8")


def load_save(path: Optional[str] = None) -> SaveData:
    file_path = Path(path or config.SAVE_FILE)
    if not file_path.exists():
        logger.info(f"No save file at {file_path}, creating defaults")
        data = SaveData()
        save_save(data, str(file_path))
        return data
    try:
        return SaveData.model_validate_json(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Failed to load save file at {file_path} ({e}), using defaults")
        return SaveData()


class Theme:
    def __init__(self, settings: ThemeSettings):
        self.draw_color = hex_to_rgb(settings.draw_color)
        self.tint_color = hex_to_rgb(settings.tint_color)
        self.bg_color = hex_to_rgb(settings.bg_color)


save_data: SaveData = load_save()
theme = Theme(save_data.theme)
player_status: PlayerStatus = save_data.player
