#Classe responsavel para controlar informações do usuario, como itens, skills SPECIAl e Exception
import json
from classes.inventory.inventory import *
import config_new as config

class VaultDweller:

    name = "Vault Dweller"
    level = 1
    exp = 0
    expMax = 10

    health = 100
    healthMax = 10

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
        "Head": 100,
        "LArm" : 100,
        "RArm" : 100,
        "LLeg" : 100,
        "RLeg" : 100
    }

    perks = []
    inventory = Inventory()
    quests = []

    def __init__(self, *args, **kwargs):
        print ("Carregando VaultDweller de arquivo json")

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
                "H":self.bodypartsCond["Head"],
                "LA":self.bodypartsCond["LArm"],
                "RA":self.bodypartsCond["RArm"],
                "LL":self.bodypartsCond["LLeg"],
                "RL":self.bodypartsCond["RLeg"],
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
        self.bodypartsCond = data['bodypartsCond']
        self.inventory.loadFrom(data["inv"])

        return self

        ##TODO
        
        #Perks
        
        #Quests