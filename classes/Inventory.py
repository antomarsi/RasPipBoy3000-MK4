from Weapon import Weapon
import abstract.Item as Item
import json

class Inventory():

    backpack = []

    #   Weapons": [],
    #     "Apparel": [],
    #     "Aid": [],
    #     "Misc": [],
    #     "Junk": [],
    #     "Mods": [],
    #     "Ammo": []

    def __init__(self):
        pass
    
    
    def addItem(self, item:Item, quantity = 1, favorited=False, equiped=False):
        self.backpack.append({"item":item,"qtd":quantity, "fav":favorited, "equip":equiped})

    def getWeapons(self):
        weapons = []
        for item in self.backpack:
            if isinstance(item["item"], Weapon)
                weapons.append(item)
        weapons.sort()
        return weapons

    def getApparels(self):
        apparels = []
            for item in self.backpack:
                if isinstance(item["item"], Appareal)
        return apparels

    def getWeight(self):
        weight = 0
        for item in self.backpack:
            weight += (item["qtd"]*item["item"].weight)
        return weight

    def toJSON(self):
        data = []
        for item in self.backpack:
            data.append({
                "baseid":item["item"].baseid,
                "qtd":item["qtd"],
                "fav":item["fav"],
                "eqp":item["equip"]
            })
        return json.dumps(data)