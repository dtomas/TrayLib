import gobject

from traylib import *
from traylib.icon import Icon
from traylib.winicon_config import WinIconConfig
from traylib.winmenu import (TYPE_SELECT, TYPE_OPTIONS, WindowMenu, 
                             WindowActionMenu) 


class WinIcon(Icon):
    """
    An L{Icon} representing a group of windows.
    You can add/remove windows using the L{add_window()} and L{remove_window()}
    methods.
    """

    def __init__(self, icon_config, win_config):
        """
        Creates a new C{WinIcon}.
        
        @param win_config: The C{WinConfig} controlling the configuration of
            the C{WinIcon}.
        """

        self.__win_config = win_config
        win_config.add_configurable(self)
        Icon.__init__(self, icon_config)

        self.__name = ''
        self.__windows = []
        self.__visible_windows = []
        self.__window_handlers = {}
        
        self.connect("destroy", self.__destroy)
        
    def is_minimized(self):
        """
        @return: {True} if all visible windows of the C{WinIcon} are minimized.
        """
        if not self.__visible_windows:
            return False
        for window in self.__visible_windows:
            if not window.is_minimized():
                return False
        return True

    def update_name(self):
        """Updates the name by calling L{make_name()}"""
        self.__name = self.make_name()
        assert (self.__name == None or isinstance(self.__name, unicode)
                or isinstance(self.__name, str))

    def update_windows(self):
        """
        Updates the list of visible windows. Also calls L{update_has_arrow()},
        L{update_tooltip()}, L{update_zoom_factor()} and
        L{update_visibility()}.
        """
        self.__visible_windows = []
        for window in self.__windows:
            if self.window_is_visible(window):
                self.__visible_windows.append(window)
        self.update_has_arrow()
        self.update_tooltip()
        self.update_zoom_factor()
        self.update_visibility()

    def update_blinking(self):
        """
        Makes the icon blink If one or more windows need attention.
        """
        for window in self.__windows:
            if window.needs_attention():
                self.set_blinking(True)
                break
        else:
            self.set_blinking(False)

    def activate_next_window(self, time = 0L):
        """
        If the active window is in the C{WinIcon}'s list of visible windows, 
        activates the window after the active window in the list of visible 
        windows. If not, the first visible window of the C{WinIcon} is 
        activated.
        """
        if not SCREEN or not self.__visible_windows:
            return False
        active_window = SCREEN.get_active_window()
        found = False
        for window in self.__visible_windows:
            if found:
                window.activate(time)
                return True
            if window == active_window:
                found = True
        self.__visible_windows[0].activate(time)
        return True

    def activate_previous_window(self, time = 0L):
        """
        If the active window is in the C{WinIcon}'s list of visible windows, 
        activates the window before the active window in the list of visible 
        windows. If not, the first visible window of the C{WinIcon} is 
        activated.
        """
        if not SCREEN or not self.__visible_windows:
            return False
        active_window = SCREEN.get_active_window()
        found = False
        last = len(self.__visible_windows) - 1
        previous_window = self.__visible_windows[last]
        for window in self.__visible_windows:
            if window == active_window:
                break
            previous_window = window
        previous_window.activate(time)
        return True

    def add_window(self, window):
        """
        Adds C{window} to the C{WinIcon}'s list of windows.
        
        @param window: The window to be added.
        """
        if window in self.__windows:
            return
        if not self.should_have_window(window):
            return
        self.__window_handlers[window] = (
                            window.connect("name_changed", 
                                        self.__window_name_changed),
                            window.connect("state_changed",
                                        self.__window_state_changed),
                            window.connect("workspace_changed",
                                        self.__window_workspace_changed))
        self.__windows.append(window)

        if self.window_is_visible(window):
            self.__visible_windows.append(window)

        self.update_has_arrow()
        self.update_zoom_factor()
        self.update_tooltip()
        self.update_visibility()
        self.update_blinking()

    def remove_window(self, window):
        """
        Removes C{window} from the C{WinIcon}'s list of windows.
        
        @param window: The window to be removed.
        """
        if window not in self.__windows:
            return
        for handler in self.__window_handlers[window]:
            window.disconnect(handler)
        del self.__window_handlers[window]
        self.__windows.remove(window)
        if window in self.__visible_windows:
            self.__visible_windows.remove(window)
        
        self.update_has_arrow()
        self.update_zoom_factor()
        self.update_tooltip()
        self.update_visibility()
        
    def window_is_visible(self, window):
        """
        @return: C{True} if the window should show up in the C{WinIcon}'s menu.
        """
        if not SCREEN:
            return False
        return (window in self.__windows
            and not window.is_skip_tasklist() 
            and (self.__win_config.all_workspaces
                or window.get_workspace() == SCREEN.get_active_workspace()
                or window.is_pinned()
                or window.is_sticky())
            or window.needs_attention())


    # Signal callbacks
    
    def __destroy(self, widget):
        self.__win_config.remove_configurable(self)

    def __window_state_changed(self, window, changed_mask, new_state):
        self.__update_window_visibility(window)
        self.update_tooltip()
        self.update_zoom_factor()
        self.update_visibility()
        self.update_has_arrow()
        if changed_mask & (wnck.WINDOW_STATE_DEMANDS_ATTENTION
                            | wnck.WINDOW_STATE_URGENT):
            self.update_blinking()

    def __window_name_changed(self, window):
        self.__update_window_visibility(window)
        self.update_tooltip()

    def __window_workspace_changed(self, window):
        self.__update_window_visibility(window)
        self.update_tooltip()
        self.update_has_arrow()
        self.update_visibility()

    def __update_window_visibility(self, window):
        if self.window_is_visible(window):
            if window not in self.__visible_windows:
                self.__visible_windows.append(window)
        else:
            if window in self.__visible_windows:
                self.__visible_windows.remove(window)


    # Methods inherited from Icon
    
    def make_visibility(self):
        """
        Determines the visibility.

        @return: C{True} if the C{WinIcon} has any visible windows or if it 
            should not hide icons with no visible windows.
        """
        return (not self.should_hide_if_no_visible_windows() 
                or self.__visible_windows)    

    def make_zoom_factor(self):
        """
        Determines the zoom factor. 
        
        @return: If the icon has the active window: C{1.5}
            If the icon has only minimized windows: half the zoom factor
            returned by C{Icon.make_zoom_factor()}
            Else: the zoom factor returned by C{Icon.make_zoom_factor()}
        """
        if self.has_active_window:
            return 1.5
        zoom_factor = Icon.make_zoom_factor(self)
        if self.is_minimized():
            zoom_factor *= 0.66
        return zoom_factor
        
    def make_has_arrow(self):
        """
        Determines whether to show an arrow or not.
        
        @return: C{True} if the icon has more than one visible window and its
            C{WinConfig} is configured to show an arrow.
        """
        return self.__win_config.arrow and len(self.__visible_windows) > 1
                
    def make_tooltip(self):
        """
        Determines the C{WinIcon}'s tooltip by calling L{make_name()}.
        
        @return: The new tooltip of the C{WinIcon}.
        """
        return self.make_name()

    def click(self, time = 0L):
        """
        If the C{WinIcon} has only one visible window, it is activated or 
        minimized, depending on its current state. If it's on a different 
        workspace, that workspace is also activated.
        
        @return: C{True} if some action could be performed.
        """
        if len(self.__visible_windows) != 1:
            return False
        window = self.__visible_windows[0]
        if self.has_active_window and not window.is_minimized():
            window.minimize()
        else:
            window.get_workspace().activate(time)
            window.unminimize(time)
            window.activate(time)
        return True

    def get_menu_left(self):
        """
        @return: The menu when the C{WinIcon} was left-clicked. 
            If it has more than one visible window, returns a L{WindowMenu} 
            where a window can be selected to be activated. Else, returns 
            C{None}.
        """
        if len(self.__visible_windows) <= 1:
            return None
        if self.has_themed_icon:
            icon = self.icon
        else:
            icon = None
        return WindowMenu(self.__visible_windows, 
                        TYPE_SELECT,
                        icon,
                        self.__name,
                        self.get_root_path(),
                        icon)

    def get_menu_right(self):
        """
        @return: The menu when the C{WinIcon} was right-clicked. 
            If it has more than one visible window, returns a L{WindowMenu} 
            with a submenu of window actions for each window.
            If there's only one visible window, returns a L{WindowActionMenu}
            for that window.
            Else, returns C{None}.
        """
        if not self.__visible_windows:
            return None
        if len(self.__visible_windows) > 1:
            if self.has_themed_icon:
                icon = self.icon
            else:
                icon = None
            return WindowMenu(self.__visible_windows, 
                        TYPE_OPTIONS,
                        icon,
                        self.__name,
                        self.get_root_path(),
                        icon,
                        has_kill = self.menu_has_kill())
        else:
            return WindowActionMenu(self.__visible_windows[0], 
                                    has_kill = self.menu_has_kill())

    def mouse_wheel_up(self, time = 0L):
        """
        Activates the next window.
        
        @return: C{True} if the next window could be activated.
        @see: WinIcon.activate_next_window()
        """
        return self.activate_next_window(time)
        
    def mouse_wheel_down(self, time = 0L):
        """
        Activates the previous window.
        
        @return: C{True} if the previous window could be activated.
        @see: L{activate_previous_window()}
        """
        return self.activate_previous_window(time)
        
    def spring_open(self, time = 0L):
        """
        Activates the next window.
        
        @return: C{True} if the next window could be activated.
        @see: L{activate_next_window()}
        """
        return self.activate_next_window(time)
        
    def should_hide_if_no_visible_windows(self):
        """
        Override this to determine whether the C{WinIcon} should hide if it has
        no visible windows anymore.
        
        @return: C{True}
        """
        return True
        
    def menu_has_kill(self):
        """
        Override this to determine whether the C{WinIcon}'s menu has a "kill" 
        menu item.
        
        @return: C{True}
        """
        return True


    # Methods called when config options of the associated WinIconConfig change

    def update_option_all_workspaces(self):
        self.update_windows()

    def update_option_arrow(self):
        self.update_has_arrow()


    # Methods to be implemented by subclasses

    def make_name(self):
        """
        Override this to determine the C{WinIcon}'s name.
        
        @return: The new name of the C{WinIcon}.
        """
        return ''

    def should_have_window(self, window):
        return True

    def get_root_path(self):
        return None


    name = property(lambda self : self.__name)
    """The C{WinIcon}'s name."""

    windows = property(lambda self : self.__windows)
    """The icon's windows."""
    
    visible_windows = property(lambda self : self.__visible_windows)
    """The list of visible windows."""
    
    has_active_window = property(lambda self : (SCREEN != None and
                                                SCREEN.get_active_window() 
                                                in self.__windows))
    """{True} if the C{WinIcon} has the active window."""

    has_visible_windows = property(lambda self : bool(self.__visible_windows))
    """{True} if the C{WinIcon} has any visible windows."""

    has_windows = property(lambda self : bool(self.__windows))
    """{True} if the C{WinIcon} has any windows."""
