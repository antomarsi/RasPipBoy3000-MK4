import abc
class IHasChild(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def add_element(self, id, element):
        return

    @abc.abstractmethod
    def get_element(self, id):
        return

