import json, config_new as config
from abc import ABCMeta, abstractmethod

class Item(metaclass=ABCMeta):

    baseid = ""
    image = None
    icon = None
    title = ""
    weight = 0
    value = 0

    @abstractmethod
    def toArray(self):
        data = {
            "baseid":self.baseid,
            "image":self.image,
            "icon":self.icon,
            "title":self.title,
            "weight":self.weight,
            "value":self.value
        }
        return data

    @abstractmethod
    def toJSON(self):
        return json.dumps(self.toArray())

    def getFromBaseid(self, baseid):
        baseitem = None
        for item in config.ITEM_DATABASE:
            if baseid == item["baseid"]:
                baseitem = item
        if baseitem == None:
            print ("Item "+baseid+" not found")
            return None
        self.image = baseitem['image']
        self.icon = baseitem['icon']
        self.title = baseitem['title']
        self.weight = baseitem['weight']
        self.value = baseitem['value']
        return baseitem


    @abstractmethod
    def draw(self):
        pass

    def __lt__(self, other):
         return self.title < other.title