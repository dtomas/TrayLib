from traylib import *
from traylib.config import Config, Attribute


class TrayConfig(Config):
    name = Attribute('update_option_name')
    """The name of the tray."""

    menus = Attribute('update_option_menus')
    """
    Where to show boxes for the main menu: C{LEFT}, C{RIGHT} or C{LEFT|RIGHT}.
    """
    separators = Attribute('update_option_separators')
    """Where to show separators (may be C{0})."""
    
    # Constructor is kept for compatibility reasons, as there might be clients
    # passing positional parameters.
    def __init__(self, name, menus, separators):
        Config.__init__(self, name=name, menus=menus, separators=separators)
