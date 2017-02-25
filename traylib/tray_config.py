from traylib import LEFT
from traylib.config import Config, Attribute


class TrayConfig(Config):
    name = Attribute()
    """The name of the tray."""

    menus = Attribute(default=LEFT)
    """Where to show a box for the main menu: C{LEFT} or C{RIGHT}."""

    separators = Attribute(default=0)
    """Where to show separators (may be C{0})."""
