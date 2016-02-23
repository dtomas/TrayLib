from traylib.config import Config, Attribute


class WinItemConfig(Config):
    all_workspaces = Attribute(default=False)
    """
    C{True}, if windows on all workspaces should be visible in the associated
    L{WinIcon}s' menus.
    """

    arrow = Attribute(default=True)
    """
    C{True}, if the L{WinIcon}s associated with the C{WinIconConfig} should
    have an arrow on them when they have more than one visible window.
    """
