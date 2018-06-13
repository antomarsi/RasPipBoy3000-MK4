#Classe responsavel para controlar informações do usuario, como itens, skills SPECIAl e Exception
import json
from classes import Inventory as inv
import config_new as config
from enum import Enum

class CondType(Enum):
    POISONED = 0
    ADDICTED = 1 
    GHOUL = 2
    OTHER = 3

class VaultDweller:

    changed = False

    name = "Vault Dweller"
    level = 1
    exp = 0
    expMax = 10

    health = 100
    healthMax = 100

    ap = 100
    apMax = 100

    caps = 55

    conditions = []

    special = {
        "Strength":     0,
        "Perception":   0,
        "Endurance":    0,
        "Charisma":     0,
        "Intelligence": 0,
        "Agility":      0,
        "Luck":         0
    }

    bodypartsCond = {
        "H": 100,
        "LA" : 100,
        "RA" : 100,
        "LL" : 100,
        "RL" : 100
    }

    perks = []
    inventory = inv.Inventory()
    quests = []

    def __init__(self, *args, **kwargs):
        print ("Carregando VaultDweller de arquivo json")

    def getEquipedWeapon(self):
        for item in self.inventory.getWeapons():
            if item["equip"]:
                return item["item"]
        return None

    def getEquipedApparels(self):
        apparels = []
        for item in self.inventory.getApparels():
            if item["equip"]:
                apparels.append(item["item"])
        return apparels

    def getBodyImage(self):
        filename = ""
        if self.bodypartsCond['LL'] == 0 and self.bodypartsCond['RL'] == 0:
            filename += "BothLeg"
        elif self.bodypartsCond['LL'] == 0:
            filename += "LeftLeg"
        elif self.bodypartsCond['RL'] == 0:
            filename += "RightLeg"
        
        if self.bodypartsCond['LA'] == 0 and self.bodypartsCond['RA'] == 0:
            filename += "BothArm"
        elif self.bodypartsCond['LA'] == 0:
            filename += "LeftArm"
        elif self.bodypartsCond['RA'] == 0:
            filename += "RightArm"

        if not filename:
            return config.IMAGES['health_cond']['Body']["Normal"]
        return config.IMAGES['health_cond']['Body'][filename]

    def getHeadImage(self):
        filename = "Normal"

        for cond in self.conditions:
            if cond.type == CondType.GHOUL:
                filename = "Ghoul"
                break
            elif cond.type == CondType.ADDICTED:
                filename = "Addicted"
                break
            elif cond.type == CondType.POISONED:
                filename = "Poisoned"
                break
        if self.bodypartsCond['H'] == 0:
            filename += "Injured"

        return config.IMAGES['health_cond']['Head'][filename]

    def toArray(self):
        data = {
            "name"  : self.name,
            "level" : self.level,
            "experience" : {
                "now": self.exp,
                "max": self.expMax
            },
            "health" : {
                "now": self.health,
                "max": self.healthMax
            },
            "ap" : {
                "now": self.ap,
                "max": self.apMax
            },
            "SPECIAL" : {
                "Strength":self.special["Strength"],
                "Perception":self.special["Perception"],
                "Endurance":self.special["Endurance"],
                "Charisma":self.special["Charisma"],
                "Intelligence":self.special["Intelligence"],
                "Agility":self.special["Agility"],
                "Luck":self.special["Luck"],
            },
            "bodypartsCond" : {
                "H":self.bodypartsCond["H"],
                "LA":self.bodypartsCond["LA"],
                "RA":self.bodypartsCond["RA"],
                "LL":self.bodypartsCond["LL"],
                "RL":self.bodypartsCond["RL"],
            },
            "conditions": [],
            "inv": {
                "Weapons": [],
                "Apparel": [],
                "Aid" : [],
                "Misc": [],
                "Junk": [],
                "Mods": [],
                "Ammo": []
            },
            "perks": [],
            "quests": []
        }

        for condition in self.conditions:
            data["conditions"].append(condition)

        data["inventory"] = self.inventory.toArray()

        for perk in self.perks:
            data["perks"].append(perk.toJSON())
        for quest in self.quests:
            data["quests"].append(quest.toJSON())

        return json.dumps(data)

    def save(self):
        with open(config.CHARACTER_JSON_FILE, 'w') as outfile:
            json.dump(self.toArray(), outfile)

    def load(self):
        data = json.load(open(config.CHARACTER_JSON_FILE))
        self.name = data['name']
        self.level = data['level']
        self.exp = data['experience']['now']
        self.expMax = data['experience']['max']
        self.health = data['health']['now']
        self.healthMax = data['health']['max']
        self.ap = data['ap']['now']
        self.apMax = data['ap']['max']
        self.SPECIAl = data['SPECIAL']
        self.bodypartsCond['H'] = data['bodypartsCond']["H"]
        self.bodypartsCond['LL'] = data['bodypartsCond']["LL"]
        self.bodypartsCond['RL'] = data['bodypartsCond']["RL"]
        self.bodypartsCond['LA'] = data['bodypartsCond']["LA"]
        self.bodypartsCond['RA'] = data['bodypartsCond']["RA"]
        self.inventory.loadFrom(data["inv"])
        self.changed = True
        return self

        ##TODO
        
        #Perks
        
        #Quests