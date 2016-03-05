from traylib.config import Config, Attribute


class WinItemConfig(Config):
    all_workspaces = Attribute(default=False)
    """
    C{True}, if windows on all workspaces should be visible in the associated
    L{AWindowsItem}s' menus.
    """

    arrow = Attribute(default=True)
    """
    C{True}, if the L{AWindowsItem}s associated with the C{WinItemConfig}
    should have an arrow on them when they have visible windows.
    """

    menu_has_kill = Attribute(default=True)
    """
    C{True} if there should be an option to kill a process in a window's menu.
    """
