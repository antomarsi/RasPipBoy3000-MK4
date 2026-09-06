from game.modules.registry import create_node


def register(pipboy):
    """Structural port only: registers the boot node tree so the old
    BaseModule/SubModule system can be fully retired, but none of these are
    reachable yet (PipBoy starts directly on config.STARTUP_MODULE). Phase 7
    wires the real content (scrolling text via Tween, vault-boy AnimationState,
    a Tween-driven progress bar) and makes `boot` the actual startup node."""
    create_node("boot", "BOOT")
    create_node("boot.boot_text", "BOOT_TEXT", parent="boot")
    create_node("boot.pip_os", "PIP_OS", parent="boot")
    create_node("boot.thumbs_up", "THUMBS_UP", parent="boot")
