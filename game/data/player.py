

from pydantic import BaseModel
from typing import Dict


class PlayerStatus(BaseModel):

    name: str = "Antomarsi"
    level: int = 1
    total_exp: int = 100
    next_level_xp: int = 201

    current_ap: int = 140
    max_ap: int = 140

    current_hp: int = 82
    max_hp: int = 85

    # SPECIAL
    strenght: int = 2
    perception: int = 9
    endurance: int = 1
    charisma: int = 1
    inteligence: int = 2
    agility: int = 8
    luck: int = 6

    radiaton: int = 0
    drugs: bool = False

    body_parts: Dict[str, float] = {
        "head": 1,
        "left_arm": 1,
        "right_arm": 1,
        "left_leg": 1,
        "right_leg": 1
    }
