import abc

class MenuInterface(metaclass=abc.ABCMeta):


    @abc.abstractmethod
    def event(self, event):
        return

    @abc.abstractmethod
    def process(self):
        return

    @abc.abstractmethod
    def draw(self):
        return
