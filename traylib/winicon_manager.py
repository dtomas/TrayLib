from traylib.winicon import WinIcon


def manage_winicons(tray, screen):

    if screen is None:
        return lambda: None, lambda: None

    window_handlers = {}

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

    def active_window_changed(screen, window=None):
        for icon in tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            icon.update_zoom_factor()

    def active_workspace_changed(screen, workspace=None):
        for icon in tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            icon.update_windows()

    class handlers:
        pass

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
        handlers.window_opened_handler = screen.connect("window_opened",
                                                     window_opened)
        handlers.window_closed_handler = screen.connect("window_closed",
                                                     window_closed)
        handlers.active_window_changed_handler = screen.connect(
            "active_window_changed", active_window_changed
        )
        handlers.active_workspace_changed_handler = (
            screen.connect("active_workspace_changed",
                           active_workspace_changed)
        )
        for window in screen.get_windows():
            window_opened(screen, window)
            yield None

    def unmanage():
        screen.disconnect(handlers.window_opened_handler)
        screen.disconnect(handlers.window_closed_handler)
        screen.disconnect(handlers.active_window_changed_handler)
        screen.disconnect(handlers.active_workspace_changed_handler)
        for window, _window_handlers in window_handlers.iteritems():
            for window_handler in _window_handlers:
                window.disconnect(window_handler)
                yield None

    return manage, unmanage
