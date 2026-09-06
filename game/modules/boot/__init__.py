from game.modules.registry import create_node
from game.modules.boot import boot_text, loading


def register(pipboy, tasks):
    """Unlike every other top-level register(pipboy), boot also takes the
    real module-loading task list (see registry.init_modules()) to hand to
    loading.py -- boot owns the startup sequence, it isn't a navigable tab
    (see registry.TOP_LEVEL). PipBoy.init_modules() enters boot.boot_text
    directly unless config.SKIP_INTRO."""
    create_node("boot", "BOOT")
    boot_text.register(pipboy)
    loading.register(pipboy, tasks)
