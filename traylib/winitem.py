import struct
from urllib import pathname2url
import os

import gobject
import gtk

from traylib import TARGET_WNCK_WINDOW_ID, TARGET_URI_LIST, ICON_THEME
from traylib.item import Item
from traylib.menu_renderer import render_menu_item
from traylib.winmenu import WindowActionMenu, WindowMenu, get_filer_window_path


def _load_icons(icon_theme):
    global dir_icon, home_icon
    home_icon = None
    dir_icon = None
    for icon_name in 'mime-inode:directory', 'folder', 'gnome-fs-directory':
        try:
            dir_icon = icon_theme.load_icon(icon_name, 32, 0)
            break
        except:
            pass
    for icon_name in 'user-home', 'gnome-fs-home':
        try:
            home_icon = icon_theme.load_icon(icon_name, 32, 0)
            break
        except:
            pass


home_icon = None
dir_icon = None
ICON_THEME.connect("changed", _load_icons)
_load_icons(ICON_THEME)


class WindowItem(Item):

    def __init__(self, win_config, window, menu_has_kill=True, root_path=None,
                 root_icon=None):
        Item.__init__(self)
        self.__win_config = win_config
        self.__window = window
        self.__menu_has_kill = menu_has_kill
        self.__root_path = root_path
        self.__root_icon = root_icon
        self.__path = get_filer_window_path(window)
        self.__window_handlers = [
            window.connect("name_changed", self.__window_name_changed),
            window.connect("state_changed", self.__window_state_changed),
        ]
        self.__screen_handlers = [
            window.get_screen().connect(
                "active-window-changed", self.__active_window_changed
            ),
            window.get_screen().connect(
                "active-workspace-changed", self.__active_workspace_changed
            ),
        ]
        self.__win_config_handlers = [
            win_config.connect(
                "all-workspaces-changed", self.__all_workspaces_changed
            ),
        ]
        self.connect("destroyed", self.__destroyed)

    def __destroyed(self, item):
        for handler in self.__window_handlers:
            self.__window.disconnect(handler)
        screen = self.__window.get_screen()
        for handler in self.__screen_handlers:
            screen.disconnect(handler)
        for handler in self.__win_config_handlers:
            self.__win_config.disconnect(handler)

    def __all_workspaces_changed(self, win_config):
        self.emit("is-visible-changed")

    def __window_state_changed(self, window, changed_mask, new_state):
        self.emit("name-changed")
        self.emit("zoom-changed")
        self.emit("is-visible-changed")
        self.emit("is-blinking-changed")

    def __window_name_changed(self, window):
        self.emit("name-changed")

    def __active_window_changed(self, screen, window=None):
        self.emit("zoom-changed")

    def __active_workspace_changed(self, screen, workspace=None):
        self.emit("is-visible-changed")

    def get_name(self):
        if self.__path:
            name = self.__path
            if self.__root_path:
                root_dirname = os.path.dirname(self.__root_path)
                if root_dirname == '/':
                    l = 1
                else:
                    l = len(root_dirname) + 1
                if name != '/':
                    name = os.path.expanduser(name)[l:]
                    name = name.replace(os.path.expanduser('~'), '~')
        else:
            name = self.__window.get_name()
        if self.__window.is_minimized():
            name = "[ " + name + " ]"
        if self.__window.is_shaded():
            name = "= " + name + " ="
        if self.__window.needs_attention():
            name = "!! " + name + " !!"
        return name.replace('_', '__')

    def get_icon_pixbuf(self):
        pixbuf = None
        if self.__path:
            icon_path = os.path.expanduser(
                os.path.join(self.__path, '.DirIcon')
            )
            if os.access(icon_path, os.F_OK):
                pixbuf = gtk.gdk.pixbuf_new_from_file(icon_path)
            elif self.__path != self.__root_path:
                if os.path.expanduser(self.__path) == os.path.expanduser('~'):
                    pixbuf = home_icon
                else:
                    pixbuf = dir_icon
            elif self.__path == self.__root_path and self.__root_icon:
                pixbuf = self.__root_icon
        if not pixbuf:
            #if self.__icon:
            #    pixbuf = icon
            #else:
            pixbuf = self.__window.get_icon()
        return pixbuf

    def get_zoom(self):
        if self.__window is self.__window.get_screen().get_active_window():
            return 1.5
        if self.__window.is_minimized():
            return 0.66
        return 1.0

    def click(self, time=0L, force_activate=False):
        window = self.__window
        active_window = window.get_screen().get_active_window()
        if (not force_activate and
                window is active_window and not window.is_minimized()):
            window.minimize()
        else:
            window.get_workspace().activate(time)
            window.unminimize(time)
            window.activate(time)
        return True

    def mouse_wheel_up(self, time=0L):
        self.__window.activate(time)

    def mouse_wheel_down(self, time=0L):
        self.__window.minimize()

    def get_menu_right(self):
        return WindowActionMenu(self.__window, has_kill=self.__menu_has_kill)

    def is_visible(self):
        window = self.__window
        screen = self.__window.get_screen()
        return (
            not window.is_skip_tasklist() and (
                self.__win_config.all_workspaces or
                window.get_workspace() == screen.get_active_workspace() or
                window.is_pinned() or window.is_sticky()
            ) or
            window.needs_attention()
        )

    def is_blinking(self):
        return self.__window.needs_attention()

    def get_drag_source_targets(self):
        targets = [("application/x-wnck-window-id", 0, TARGET_WNCK_WINDOW_ID)]
        if self.__path:
            targets.append(("text/uri-list", 0, TARGET_URI_LIST))
        return targets

    def get_drag_source_actions(self):
        actions = gtk.gdk.ACTION_MOVE
        if self.__path:
            actions |= gtk.gdk.ACTION_COPY
            actions |= gtk.gdk.ACTION_LINK
        return actions

    def drag_data_get(self, context, data, info, time):
        if info == TARGET_WNCK_WINDOW_ID:
            xid = self.__window.get_xid()
            data.set(data.target, 8, apply(struct.pack, ['1i', xid]))
        else:
            data.set_uris(
                ['file://%s' % pathname2url(os.path.expanduser(self.__path))]
            )

    @property
    def window(self):
        return self.__window

    @property
    def root_path(self):
        return self.__root_path


class WindowsItem(Item):

    def __init__(self, win_config, screen, name, menu_has_kill=True,
                 root_path=None, root_icon=None):
        Item.__init__(self)
        self.__win_config = win_config
        self.__name = name
        self.__screen = screen
        self.__menu_has_kill = menu_has_kill
        self.__root_path = root_path
        self.__root_icon = root_icon
        self.__window_items = []
        self.__window_handlers = {}
        self.__screen_handlers = [
            self.__screen.connect(
                "active-window-changed", self.__active_window_changed
            )
        ]
        self.__win_config_handlers = [
            win_config.connect("arrow-changed", self.__arrow_changed),
        ]
        self.connect("destroyed", self.__destroyed)

    def __destroyed(self, item):
        for handler in self.__screen_handlers:
            self.__screen.disconnect(handler)
        for handler in self.__win_config_handlers:
            self.__win_config.disconnect(handler)
        for window, handlers in self.__window_handlers.iteritems():
            for window_item in self.__window_items:
                if window is window_item.window:
                    for handler in handlers:
                        window_item.disconnect(handler)
                    break
        for window_item in self.__window_items:
            window_item.destroy()

    def __arrow_changed(self, win_config):
        self.emit("has-arrow-changed")

    def __active_window_changed(self, screen, window=None):
        self.emit("zoom-changed")

    def add_window(self, window):
        for window_item in self.__window_items:
            if window_item.window is window:
                return
        window_item = WindowItem(
            self.__win_config, window, self.__menu_has_kill, self.__root_path,
            self.__root_icon
        )
        self.__window_handlers[window] = [
            window_item.connect(
                "is-visible-changed", self.__window_visible_changed
            ),
            window_item.connect(
                "is-blinking-changed", self.__window_blinking_changed
            ),
        ]
        self.__window_items.append(window_item)
        self.emit("has-arrow-changed")
        self.emit("is-visible-changed")
        self.emit("menu-left-changed")
        self.emit("menu-right-changed")
        self.emit("drag-source-changed")
        self.emit("zoom-changed")
        self.emit("name-changed")
        self.emit("visible-window-items-changed")

    def __window_visible_changed(self, window_item):
        self.emit("is-visible-changed")
        self.emit("has-arrow-changed")
        self.emit("menu-left-changed")
        self.emit("menu-right-changed")
        self.emit("drag-source-changed")
        self.emit("zoom-changed")
        self.emit("name-changed")
        self.emit("visible-window-items-changed")

    def __window_blinking_changed(self, window_item):
        self.emit("is-blinking-changed")

    def remove_window(self, window):
        try:
            handlers = self.__window_handlers.pop(window)
        except KeyError:
            return
        else:
            for window_item in self.__window_items:
                if window is window_item.window:
                    for handler in handlers:
                        window_item.disconnect(handler)
            self.__window_items = [
                item for item in self.__window_items if item.window != window
            ]
            self.emit("has-arrow-changed")
            self.emit("is-visible-changed")
            self.emit("menu-left-changed")
            self.emit("menu-right-changed")
            self.emit("drag-source-changed")
            self.emit("zoom-changed")
            self.emit("name-changed")
            self.emit("visible-window-items-changed")

    def has_arrow(self):
        return self.__win_config.arrow and len(self.visible_window_items) > 1

    def get_menu_left(self):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) <= 1:
            return None
        menu = gtk.Menu()
        for item in visible_window_items:
            menu.append(render_menu_item(item))
        return menu

    def get_menu_right(self):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) == 1:
            return visible_window_items[0].get_menu_right()
        return WindowMenu(
            visible_window_items, self.__screen, self.get_name(),
            root=self.__root_path,
            root_icon=self.__root_icon,
            has_kill=self.__menu_has_kill,
        )

    def activate_next_window(self, time=0L):
        """
        If the active window is in the C{WindowsItem}'s list of windows, 
        activates the window after the active window in the list of visible 
        windows. If not, the first visible window of the C{WindowsItem} is 
        activated.
        """
        visible_window_items = self.visible_window_items
        if not self.__screen or not visible_window_items:
            return False
        active_window = self.__screen.get_active_window()
        found = False
        for window_item in visible_window_items:
            if found:
                window_item.click(time, force_activate=True)
                return True
            if window_item.window is active_window:
                found = True
        visible_window_items[0].click(time, force_activate=True)
        return True

    def activate_previous_window(self, time=0L):
        """
        If the active window is in the C{WindowsItem}'s list of windows, 
        activates the window before the active window in the list of visible 
        windows. If not, the first visible window of the C{WindowsItem} is 
        activated.
        """
        visible_window_items = self.visible_window_items
        if not self.__screen or not visible_window_items:
            return False
        active_window = self.__screen.get_active_window()
        found = False
        last = len(visible_window_items) - 1
        previous_window_item = visible_window_items[last]
        for window_item in visible_window_items:
            if window_item.window is active_window:
                break
            previous_window_item = window_item
        previous_window_item.click(time, force_activate=True)
        return True

    def mouse_wheel_up(self, time=0L):
        return self.activate_next_window(time)

    def mouse_wheel_down(self, time=0L):
        return self.activate_previous_window(time)

    def click(self, time=0L):
        return self.visible_window_items[0].click(time)

    def spring_open(self, time=0L):
        self.mouse_wheel_up(time)

    def is_visible(self):
        return len(self.visible_window_items) > 0

    def is_blinking(self):
        for window_item in self.visible_window_items:
            if window_item.is_blinking():
                return True
        return False

    def get_zoom(self):
        active_window = self.__screen.get_active_window()
        visible_window_items = self.visible_window_items
        for window_item in visible_window_items:
            if window_item.window is active_window:
                return 1.5
        for window_item in visible_window_items:
            if not window_item.window.is_minimized():
                break
        else:
            return 0.66
        return 1.0

    def get_name(self):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) == 1:
            return visible_window_items[0].get_name()
        return "%s (%d)" % (self.__name, len(visible_window_items))

    def get_drag_source_targets(self):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) > 0:
            return visible_window_items[0].get_drag_source_targets()
        return []

    def get_drag_source_actions(self):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) > 0:
            return visible_window_items[0].get_drag_source_actions()
        return 0

    def drag_data_get(self, context, data, info, time):
        self.visible_window_items[0].drag_data_get(context, data, info, time)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name
        self.emit("name-changed")

    @property
    def window_items(self):
        return self.__window_items

    @property
    def visible_window_items(self):
        return [item for item in self.__window_items if item.is_visible()]

gobject.type_register(WindowsItem)
gobject.signal_new(
    "visible-window-items-changed", WindowsItem, gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, ()
)
