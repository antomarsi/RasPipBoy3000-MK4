from classes.abstract.Item import Item

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
