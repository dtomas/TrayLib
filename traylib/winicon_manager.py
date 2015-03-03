from traylib.winicon import WinIcon
from traylib.gui.icon_manager import IconManager
from traylib import SCREEN


class WinIconManager(IconManager):
    
    def __init__(self, tray, screen):
        IconManager.__init__(self, tray)
        self.__screen = screen
        self.__window_handlers = {}

    def init(self):
        screen = self.__screen
        self.__window_opened_handler = screen.connect("window_opened", self.__window_opened)
        self.__window_closed_handler = screen.connect("window_closed", self.__window_closed)
        self.__active_window_changed_handler = screen.connect("active_window_changed", 
                                        self.__active_window_changed)
        self.__active_workspace_changed_handler = screen.connect("active_workspace_changed",
                                        self.__active_workspace_changed)
        
        for window in screen.get_windows():
            self.__window_opened(screen, window)
            yield None

    def quit(self):
        screen = self.__screen
        screen.disconnect(self.__window_opened_handler)
        screen.disconnect(self.__window_closed_handler)
        screen.disconnect(self.__active_window_changed_handler)
        screen.disconnect(self.__active_workspace_changed_handler)
        for window, window_handlers in self.__window_handlers.iteritems():
            for window_handler in window_handlers:
                window.disconnect(window_handler)
                yield None
                
    def icon_added(self, icon):
        if not isinstance(icon, WinIcon):
            return
        screen = self.__screen
        for window in screen.get_windows():
            if icon.should_have_window(window):
                icon.add_window(window)

    def __window_opened(self, screen, window):
        self.__window_handlers[window] = [window.connect("name_changed",
                                            self.__window_name_changed)]
        for icon in self.__tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            if icon.should_have_window(window):
                icon.add_window(window)

    def __window_name_changed(self, window):
        for icon in self.__tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            if icon.should_have_window(window):
                icon.add_window(window)
            else:
                icon.remove_window(window)

    def __window_closed(self, screen, window):
        for icon in self.__tray.icons:
            icon.remove_window(window)
        for handler in self.__window_handlers[window]:
            window.disconnect(handler)
        self.__window_handlers[window] = []

    def __active_window_changed(self, screen, window = None):
        for icon in self.__tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            icon.update_zoom_factor()

    def __active_workspace_changed(self, screen, workspace = None):
        for icon in self.__tray.icons:
            if not isinstance(icon, WinIcon):
                continue
            icon.update_windows()
