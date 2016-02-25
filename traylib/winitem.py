import struct
from urllib import pathname2url
import os

import gobject
import gtk

from traylib import TARGET_WNCK_WINDOW_ID, TARGET_URI_LIST, ICON_THEME
from traylib.item import Item
from traylib.menu_renderer import render_menu_item
from traylib.winmenu import WindowActionMenu, WindowMenu
from traylib.icons import FileIcon, ThemedIcon, PixbufIcon


class WindowItem(Item):

    def __init__(self, window, win_config):
        Item.__init__(self)
        self.__window = window
        self.__win_config = win_config
        self.__window_handlers = [
            window.connect("name-changed", self.__window_name_changed),
            window.connect("state-changed", self.__window_state_changed),
            window.connect(
                "workspace-changed", self.__window_workspace_changed
            ),
            window.connect("icon-changed", self.__window_icon_changed),
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


    # Signal callbacks:

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

    def __window_workspace_changed(self, window):
        self.emit("is-visible-changed")
        self.emit("icon-changed")

    def __window_icon_changed(self, window):
        self.emit("icon-changed")

    def __window_name_changed(self, window):
        self.emit("name-changed")

    def __active_window_changed(self, screen, window=None):
        self.emit("zoom-changed")

    def __active_workspace_changed(self, screen, workspace=None):
        self.emit("is-visible-changed")
        self.emit("icon-changed")


    # Item implementation:

    def get_name(self):
        name = self.get_base_name()
        if self.__window.is_minimized():
            name = "[ " + name + " ]"
        if self.__window.is_shaded():
            name = "= " + name + " ="
        if self.__window.needs_attention():
            name = "!! " + name + " !!"
        return name.replace('_', '__')

    def get_icons(self):
        return [PixbufIcon(self.__window.get_icon())]

    def is_greyed_out(self):
        return (
            not self.is_on_active_workspace() and
            not self.__window.needs_attention()
        )

    def is_on_active_workspace(self):
        window = self.__window
        screen = window.get_screen()
        workspace = window.get_workspace()
        return (
            workspace is screen.get_active_workspace() or
            window.is_pinned() or window.is_sticky()
        )

    def get_zoom(self):
        if self.__window.is_active():
            return 1.5
        if self.__window.is_minimized():
            return 0.66
        return 1.0

    def click(self, time=0L, force_activate=False):
        window = self.__window
        if (not force_activate and
                window.is_active() and not window.is_minimized()):
            window.minimize()
        else:
            self.activate(time)
        return True

    def activate(self, time=0L):
        window = self.__window
        window.get_workspace().activate(time)
        window.unminimize(time)
        window.activate(time)

    def mouse_wheel_up(self, time=0L):
        self.activate(time)

    def mouse_wheel_down(self, time=0L):
        self.__window.minimize()

    def get_menu_right(self):
        has_kill = self.__win_config.menu_has_kill
        pid = self.__window.get_pid()
        if pid != 0 and has_kill:
            # Only show kill menu item if there are no other windows of the
            # same process.
            for window in self.__window.get_screen().get_windows():
                if window != self.__window and window.get_pid() == pid:
                    has_kill = False
                    break
        return WindowActionMenu(self.__window, has_kill=has_kill)

    def is_visible(self):
        window = self.__window
        screen = self.__window.get_screen()
        return (
            not window.is_skip_tasklist() and (
                self.__win_config.all_workspaces or
                self.is_on_active_workspace()
            ) or
            window.needs_attention()
        )

    def is_blinking(self):
        return self.__window.needs_attention()

    def get_drag_source_targets(self):
        return [("application/x-wnck-window-id", 0, TARGET_WNCK_WINDOW_ID)]

    def get_drag_source_actions(self):
        return gtk.gdk.ACTION_MOVE

    def drag_data_get(self, context, data, info, time):
        if info == TARGET_WNCK_WINDOW_ID:
            xid = self.__window.get_xid()
            data.set(data.target, 8, apply(struct.pack, ['1i', xid]))


    # Methods which may be overridden by subclasses:

    def get_base_name(self):
        return self.__window.get_name()


    # Properties:

    @property
    def window(self):
        return self.__window


class ADirectoryWindowItem(WindowItem):

    def __init__(self, window, win_config):
        WindowItem.__init__(self, window, win_config)
        self.__window_handlers = [
            window.connect("name-changed", self.__window_name_changed),
        ]
        self.connect("path-changed", self.__path_changed)
        self.connect("destroyed", self.__destroyed)


    # Signal callbacks:

    def __destroyed(self, item):
        for handler in self.__window_handlers:
            self.__window.disconnect(handler)

    def __path_changed(self, item):
        self.emit("name-changed")
        self.emit("icon-changed")

    def __window_name_changed(self, window):
        self.emit("path-changed")


    # Item implementation:

    def get_icons(self):
        path = self.get_path()
        icons = [
            FileIcon(
                os.path.expanduser(os.path.join(path, '.DirIcon'))
            ),
        ]
        if os.path.expanduser(path) == os.path.expanduser('~'):
            icons += [ThemedIcon('user-home'), ThemedIcon('gnome-fs-home')]
        else:
            icons += [
                ThemedIcon('mime-inode:directory'),
                ThemedIcon('folder'),
                ThemedIcon('gnome-fs-directory')
            ]
        icons += WindowItem.get_icons(self)
        return icons

    def get_drag_source_targets(self):
        return WindowItem.get_drag_source_targets(self) + [
            ("text/uri-list", 0, TARGET_URI_LIST)
        ]

    def get_drag_source_actions(self):
        return (
            WindowItem.get_drag_source_actions(self) |
            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK
        )

    def drag_data_get(self, context, data, info, time):
        WindowItem.drag_data_get(self, context, data, info, time)
        if info == TARGET_URI_LIST:
            data.set_uris([
                'file://%s' % pathname2url(os.path.expanduser(self.get_path()))
            ])


    # WindowItem implementation:

    def get_base_name(self):
        return self.get_path()


    # Methods to be implemented by subclasses:

    def get_path(self):
        raise NotImplementedError


gobject.type_register(ADirectoryWindowItem)
gobject.signal_new(
    "path-changed", ADirectoryWindowItem, gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, ()
)


class FilerDirectoryWindowItem(ADirectoryWindowItem):

    def get_path(self):
        name = self.window.get_name()
        for i in range(1-len(name), 0):
            if name[-i] == '(' or name[-i] == '+':
                name = name[:-(i+1)]
                break
        return name


def is_filer_window(window):
    name = window.get_name()
    return (
        window.get_class_group().get_name() == 'ROX-Filer' and
        name.startswith('/') or name.startswith('~')
    )


def create_window_item(window, win_config):
    name = window.get_name()
    if is_filer_window(window):
        return FilerDirectoryWindowItem(window, win_config)
    return WindowItem(window, win_config)


class AWindowsItem(Item):

    def __init__(self, win_config, screen):
        Item.__init__(self)
        self.__win_config = win_config
        self.__screen = screen
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


    # Signal callbacks:

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
        if screen.get_active_window() is not None:
            self.emit("icon-changed")

    def __window_visible_changed(self, window_item):
        self.emit("is-visible-changed")
        self.emit("has-arrow-changed")
        self.emit("menu-left-changed")
        self.emit("menu-right-changed")
        self.emit("drag-source-changed")
        self.emit("zoom-changed")
        self.emit("name-changed")
        self.emit("icon-changed")
        self.emit("visible-window-items-changed")
        self.emit("is-greyed-out-changed")

    def __window_blinking_changed(self, window_item):
        self.emit("is-blinking-changed")

    def __window_greyed_out_changed(self, window_item):
        self.emit("is-greyed-out-changed")

    def __window_icon_changed(self, window_item):
        self.emit("icon-changed")


    # Public methods (don't override these):

    def add_window(self, window):
        for window_item in self.__window_items:
            if window_item.window is window:
                return
        window_item = self.create_window_item(window)
        self.__window_handlers[window] = [
            window_item.connect(
                "is-visible-changed", self.__window_visible_changed
            ),
            window_item.connect(
                "is-blinking-changed", self.__window_blinking_changed
            ),
            window_item.connect(
                "icon-changed", self.__window_icon_changed
            ),
            window_item.connect(
                "is-greyed-out-changed", self.__window_greyed_out_changed
            ),
        ]
        self.__window_items.append(window_item)
        self.__window_items.sort(
            key=lambda window_item: window_item.window.get_sort_order()
        )
        self.emit("has-arrow-changed")
        self.emit("is-visible-changed")
        self.emit("menu-left-changed")
        self.emit("menu-right-changed")
        self.emit("drag-source-changed")
        self.emit("zoom-changed")
        self.emit("name-changed")
        self.emit("visible-window-items-changed")
        self.emit("is-greyed-out-changed")

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
                item for item in self.__window_items
                if item.window is not window
            ]
            self.emit("has-arrow-changed")
            self.emit("is-visible-changed")
            self.emit("menu-left-changed")
            self.emit("menu-right-changed")
            self.emit("drag-source-changed")
            self.emit("zoom-changed")
            self.emit("name-changed")
            self.emit("visible-window-items-changed")
            self.emit("is-greyed-out-changed")

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
        found = False
        for window_item in visible_window_items:
            if found:
                window_item.click(time, force_activate=True)
                return True
            if window_item.window.is_active():
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
        found = False
        last = len(visible_window_items) - 1
        previous_window_item = visible_window_items[last]
        for window_item in visible_window_items:
            if window_item.window.is_active():
                break
            previous_window_item = window_item
        previous_window_item.click(time, force_activate=True)
        return True


    # Item implementation:

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
            has_kill=self.__win_config.menu_has_kill,
        )

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
        visible_window_items = self.visible_window_items
        for window_item in visible_window_items:
            if window_item.window.is_active():
                return 1.5
        for window_item in visible_window_items:
            if not window_item.window.is_minimized():
                break
        else:
            return 0.66
        return 1.0

    def is_greyed_out(self):
        for window_item in self.visible_window_items:
            if not window_item.is_greyed_out():
                return False
        return True

    def get_name(self):
        visible_window_items = self.visible_window_items
        if len(visible_window_items) == 1:
            return self.get_base_name()
        return "%s (%d)" % (self.get_base_name(), len(visible_window_items))

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


    # Methods which may be overridden by subclasses:

    def create_window_item(self, window):
        return create_window_item(window, self.__win_config)


    # Abstract methods to be implemented by subclasses:

    def get_icons(self):
        raise NotImplementedError

    def get_base_name(self):
        raise NotImplementedError


    # Properties:

    win_config = property(lambda self: self.__win_config)

    window_items = property(lambda self: self.__window_items)

    @property
    def visible_window_items(self):
        return [item for item in self.__window_items if item.is_visible()]


gobject.type_register(AWindowsItem)
gobject.signal_new(
    "visible-window-items-changed", AWindowsItem, gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, ()
)
