from classes.Items import Apparel, Ammo, Junk, Misc, Mods, Weapon
import classes.abstract.Item as Item
import importlib
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

    def __init__(self, loader = []):
        print(loader)
    
    def loadFrom(self, data):
        self.backpack.clear()
        for key, value in data.items():
            module = importlib.import_module("classes.Items")
            class_ = getattr(module, key)
            for item in value:
                i = class_()
                i.getFromBaseid(item['baseid'])
                self.add_item(i, item['qtd'], item['fav'], item['eqp'])

    def add_item(self, item: Item, quantity = 1, favorited=False, equiped=False):
        self.backpack.append({"item":item,"qtd":quantity, "fav":favorited, "equip":equiped})

    def removeItem(self, baseid, quantity = 1):
        for index, item in self.backpack:
            if item.baseid == baseid:
                if item.quantity <= quantity:
                    self.backpack.remove(item)
                else:
                    self.backpack[index].quantity -= quantity
                return True
        return False

    def getApparels(self):
        array = []
        for item in self.backpack:
            if isinstance(item["item"], Apparel):
                array.append(item)
        array.sort()
        return array

    def getAmmo(self):
        array = []
        for item in self.backpack:
            if isinstance(item["item"], Ammo):
                array.append(item)
        array.sort()
        return array

    def getJunk(self):
        array = []
        for item in self.backpack:
            if isinstance(item["item"], Junk):
                array.append(item)
        array.sort()
        return array

    def getMisc(self):
        array = []
        for item in self.backpack:
            if isinstance(item["item"], Misc):
                array.append(item)
        array.sort()
        return array

    def getMods(self):
        array = []
        for item in self.backpack:
            if isinstance(item["item"], Mods):
                array.append(item)
        array.sort()
        return array

    def getWeapons(self):
        array = []
        for item in self.backpack:
            if isinstance(item["item"], Weapon):
                array.append(item)
        array.sort()
        return array

    def getWeight(self):
        weight = 0
        for item in self.backpack:
            weight += (item["qtd"]*item["item"].weight)
        return weight

    def toArray(self):
        data = []
        for item in self.backpack:
            data.append({
                "baseid":item["item"].baseid,
                "qtd":item["qtd"],
                "fav":item["fav"],
                "eqp":item["equip"]
            })
        return data

    def toJSON(self):
        return json.dumps(self.toArray())
