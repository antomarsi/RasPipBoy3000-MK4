from game.modules.registry import create_node
from game.modules.stat import perks, special, status


def register(pipboy):
    create_node("stat", "STAT")
    status.register(pipboy)
    special.register(pipboy)
    perks.register(pipboy)
