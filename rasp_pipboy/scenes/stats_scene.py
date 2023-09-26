
from rasp_pipboy.core.scene_base import SceneBase
from rasp_pipboy.core.resource_loader import ResourceLoader
import os

class StatusScene(SceneBase):

    def __init__(self):
        super().__init__()
        health_conditions = [
            "broken_LA_RA_LL_RL",
            "broken_BLA_RA_LL_RL",
            "broken_LA_BRA_LL_RL",
            "broken_BLA_BRA_LL_RL",
            "broken_LA_RA_BLL_RL",
            "broken_BLA_RA_BLL_RL",
            "broken_LA_BRA_BLL_RL",
            "broken_BLA_BRA_LL_RL",
            "broken_LA_RA_LL_BRL",
            "broken_BLA_RA_LL_BRL",
            "broken_LA_BRA_LL_BRL",
            "broken_BLA_BRA_LL_BRL",
            "broken_LA_RA_BLL_BRL",
            "broken_BLA_RA_BLL_BRL",
            "broken_LA_BRA_BLL_BRL",
            "broken_BLA_BRA_BLL_BRL",
        ]
        head_conditions = [
            "head",
            "head_low",
            "head_addicted",
            "head_radiation",
            "head_b",
            "head_b_addicted",
            "head_b_radiation"
        ]
        status_icons = [
            "damage_resistence",
            "poison_resistence",
            "fire_resistence",
            "energy_resistence",
            "freeze_resistence",
            "radiation_resistence",
            "damage",
            "gun",
            "helmet"
        ]
        
        print("loading health cond")
        for index, icon in enumerate(health_conditions):
            ResourceLoader.getInstance().add_image(icon, os.path.join("img", "health_cond", f"icon_condition_body_{index}.png"))
        print("loading head health cond")
        for index, icon in enumerate(head_conditions):
            ResourceLoader.getInstance().add_image(icon, os.path.join("img", "health_cond", f"icon_condition_head_{index}.png"))
        print("loading status icons")
        for index, icon in enumerate(status_icons):
            ResourceLoader.getInstance().add_image(icon, os.path.join("img", "stats", f"icon_{index}.png"))

class StatsScene(SceneBase):

    def __init__(self):
        super().__init__()
        self.add_entity("status", StatusScene())
        
            