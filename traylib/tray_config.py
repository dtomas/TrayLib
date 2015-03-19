from traylib import LEFT
from traylib.config import Config, Attribute


class TrayConfig(Config):
    name = Attribute()
    """The name of the tray."""

    menus = Attribute(default=LEFT)
    """
    Where to show boxes for the main menu: C{LEFT}, C{RIGHT} or C{LEFT|RIGHT}.
    """
    separators = Attribute(default=0)
    """Where to show separators (may be C{0})."""
