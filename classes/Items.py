from classes.abstract.Item import Item
from enum import Enum

class ArmorType(Enum):
    NONE = 0
    CHESTPLACE = 1 
    LEFT_ARM = 2
    RIGHT_ARM = 3
    LEFT_LEG = 4
    RIGHT_LEG = 5
    GOOGLES = 6
    HELMET = 7
    MASK = 8
    SHIRT = 9
    JUMPSUIT = 10

class Aid(Item):

    hpRestore = 0
    rads = 0
    addedEffects = []

    def getFromBaseid(self, baseid):
        baseitem = super().getFromBaseid(baseid)

        self.hpRestore = baseitem["hpRestore"]
        self.rads = baseitem["rads"]
        self.addedEffects = baseitem["effects"]

        return baseitem

    def toArray(self):
        data = super().toArray()
        data["hpRestore"] = self.hpRestore
        data["rads"] = self.rads
        data["effects"] = self.addedEffects
        return data

    def draw(self):
        super()

    def toJSON(self):
        super()

class Ammo(Item):

    def draw(self):
        super()

    def toJSON(self):
        super()

class Apparel(Item):

    damageResistence = 0
    eletricResistence = 0
    radiationResistence = 0
    armorType = ArmorType(0)

    def __init__(self):
        pass

    def getFromBaseid(self, baseid):
        baseitem = super().getFromBaseid(baseid)

        self.damageResistence = baseitem["DR"]
        self.eletricResistence = baseitem["ER"]
        self.radiationResistence = baseitem["RR"]
        self.armorType = ArmorType(baseitem["armorType"])
        return baseitem

    def toArray(self):
        data = super().toArray()
        data["DR"] = self.damageResistence
        data["ER"] = self.eletricResistence
        data["RR"] = self.radiationResistence
        data["armorType"] = self.armorType
        return data

    def draw(self):
        super()

    def toJSON(self):
        super()

class Junk(Item):

    def draw(self):
        super()

    def toJSON(self):
        super()

class Misc(Item):

    def draw(self):
        super()

    def toJSON(self):
        super()

class Mods(Item):

    def draw(self):
        super()

    def toJSON(self):
        super()

class Weapon(Item):
    
    fire_rate = 0
    range_distance = 0
    accuracy = 60
    damage = 18
    ammo = ""

    def __init__(self):
        pass

    def getFromBaseid(self, baseid):
        baseitem = super().getFromBaseid(baseid)

        self.fire_rate = baseitem["fire_rate"]
        self.range_distance = baseitem["range_distance"]
        self.accuracy = baseitem["accuracy"]
        self.damage = baseitem["damage"]
        self.ammo = baseitem["ammo"]

        return baseitem

    def toArray(self):
        data = super().toArray()
        data["fire_rate"] = self.fire_rate
        data["range_distance"] = self.range_distance
        data["accuracy"] = self.accuracy
        data["damage"] = self.damage
        data["ammo"] = self.ammo

        return data

    def draw(self):
        super()

    def toJSON(self):
        super()
