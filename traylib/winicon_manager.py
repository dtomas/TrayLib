from traylib.winicon import WinIcon


def manage_winicons(tray, screen):
    """
    Tray manager adding/removing opened windows to/from L{WinIcon}s in the
    tray.

    To be used with L{ManagedTray}, example::

        tray = ManagedTray(
            icon_config, tray_config, managers=[
                partial(manage_winicons, screen=wnck.screen_get_default())
            ]
        )

    @param tray: The L{Tray} to manage.
    @param screen: The C{wnck.Screen} providing the windows.

    @return: Pair of generator functions manage(tray), unmanage(tray)
    """

    if screen is None:
        return lambda: None, lambda: None

    window_handlers = {}
    screen_handlers = []

    def window_opened(screen, window):
        window_handlers[window] = [
            window.connect("name_changed", window_name_changed)
        ]
        for icon in tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            if icon.should_have_window(window):
                icon.add_window(window)

    def window_name_changed(window):
        for icon in tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            if icon.should_have_window(window):
                icon.add_window(window)
            else:
                icon.remove_window(window)

    def window_closed(screen, window):
        for icon in tray.icons:
            icon.remove_window(window)
        for handler in window_handlers[window]:
            window.disconnect(handler)
        window_handlers[window] = []

    def icon_added(tray, icon):
        if not isinstance(icon, WinIcon):
            return
        if screen is None:
            return
        for window in screen.get_windows():
            if icon.should_have_window(window):
                icon.add_window(window)

    tray.connect("icon-added", icon_added)

    def manage():
        screen_handlers.append(
            screen.connect("window_opened", window_opened)
        )
        screen_handlers.append(
            screen.connect("window_closed", window_closed)
        )
        for window in screen.get_windows():
            window_opened(screen, window)
            yield None

    def unmanage():
        for handler in screen_handlers:
            screen.disconnect(handler)
        for window, _window_handlers in window_handlers.iteritems():
            for window_handler in _window_handlers:
                window.disconnect(window_handler)
                yield None

    return manage, unmanage
