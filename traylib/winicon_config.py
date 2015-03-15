from traylib import *
from traylib.config import Config, Attribute


class WinIconConfig(Config):
    all_workspaces = Attribute('update_option_all_workspaces')
    """
    C{True}, if windows on all workspaces should be visible in the associated
    L{WinIcon}s' menus.
    """

    arrow = Attribute('update_option_arrow')
    """
    C{True}, if the L{WinIcon}s associated with the C{WinIconConfig} should
    have an arrow on them when they have more than one visible window.
    """

    # Constructor is kept for compatibility reasons, as there might be clients
    # passing positional parameters.
    def __init__(self, all_workspaces, arrow):
        Config.__init__(self, all_workspaces=all_workspaces, arrow=arrow)
