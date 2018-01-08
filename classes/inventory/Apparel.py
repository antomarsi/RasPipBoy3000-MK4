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

class Apparel(Item):

    damageResistence = 0
    eletricResistance = 0
    radiationResistance = 0
    armorType = ArmorType(0)

    def __init__(self):
        pass

    def getFromBaseid(self, baseid):
        baseitem = super().getFromBaseid(baseid)

        self.damageResistence = baseitem["DR"]
        self.eletricResistance = baseitem["ER"]
        self.radiationResistance = baseitem["RR"]
        self.armorType = ArmorType(baseitem["armorType"])
        return baseitem

    def toArray(self):
        data = super().toArray()
        data["DR"] = self.damageResistence
        data["ER"] = self.eletricResistance
        data["RR"] = self.radiationResistance
        data["armorType"] = self.armorType
        return data

    def draw(self):
        super()

    def toJSON(self):
        super()
