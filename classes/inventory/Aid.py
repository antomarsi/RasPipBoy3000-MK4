from classes.abstract.Item import Item

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
