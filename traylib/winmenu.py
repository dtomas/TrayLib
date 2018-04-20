import os
import struct
from urllib.request import pathname2url

from gi.repository import Gtk

import rox

from traylib import (
    ICON_THEME, TARGET_WNCK_WINDOW_ID, TARGET_URI_LIST, Wnck, _
)
from traylib.menu_renderer import render_menu_item
from traylib.pixbuf_helper import scale_pixbuf_to_size


def _kill(menu_item, pids, name):
    if rox.confirm(
            _("Really force %s to quit?") % name,
            Gtk.STOCK_QUIT, _("Force quit")):
        for pid in pids:
            rox.processes.PipeThroughCommand(
                ('kill', '-KILL', str(pid)), None, None
            ).wait()


class WindowActionMenu(Gtk.Menu):
    """A menu that shows actions for a C{Wnck.Window}."""

    def __init__(self, window, has_kill=False):
        """
        Initialize a C{WindowActionMenu}.
        
        @param has_kill: If C{True}, the menu contains an entry to kill the 
            process the window belongs to.
        """
        Gtk.Menu.__init__(self)
    
        self.__window = window
        screen = window.get_screen()
    
        item = Gtk.MenuItem.new_with_label(_("Activate"))
        item.connect(
            "activate",
            lambda item: window.activate(Gtk.get_current_event_time())
        )
        self.append(item)
    
        self.append(Gtk.SeparatorMenuItem())

        actions = window.get_actions()        

        if window.is_maximized():
            item = Gtk.MenuItem.new_with_label(_("Unmaximize"))
            item.connect("activate", lambda item: window.unmaximize())
            item.set_sensitive(Wnck.WindowActions.UNMAXIMIZE & actions)
        else:
            item = Gtk.MenuItem.new_with_label(_("Maximize"))
            item.connect("activate", lambda item: window.maximize())
            item.set_sensitive(Wnck.WindowActions.MAXIMIZE & actions)
        self.append(item)
    
        if window.is_minimized():
            item = Gtk.MenuItem.new_with_label(_("Show"))
            item.connect(
                "activate",
                lambda item: window.unminimize(Gtk.get_current_event_time())
            )
        else:
            item = Gtk.MenuItem.new_with_label(_("Hide"))
            item.connect("activate", self.__minimize)
        self.append(item)
    
        if window.is_shaded():
            item = Gtk.MenuItem.new_with_label(_("Unshade"))
            item.connect("activate", lambda item: window.unshade())
            item.set_sensitive(Wnck.WindowActions.UNSHADE & actions)
        else:
            item = Gtk.MenuItem.new_with_label(_("Shade"))
            item.connect("activate", lambda item: window.shade())
            item.set_sensitive(Wnck.WindowActions.SHADE & actions)
        self.append(item)
    
        self.append(Gtk.SeparatorMenuItem())
    
        if window.is_pinned() or window.is_sticky():
            item = Gtk.MenuItem.new_with_label(_("Only on this workspace"))
            item.connect("activate", lambda item: window.unstick())
            item.connect("activate", lambda item: window.unpin())
            item.set_sensitive(Wnck.WindowActions.UNSTICK & actions)
        else:
            item = Gtk.MenuItem.new_with_label(_("Always on visible workspace"))
            item.connect("activate", lambda item: window.stick())
            item.connect("activate", lambda item: window.pin())
            item.set_sensitive(Wnck.WindowActions.STICK & actions)
        self.append(item)
    
        if screen.get_workspace_count() > 1:
            item = Gtk.MenuItem.new_with_label(_("Move to workspace"))
            self.append(item)
            submenu = Gtk.Menu()
            item.set_submenu(submenu)
            for i in range(0, screen.get_workspace_count()):
                workspace = screen.get_workspace(i)
                item = Gtk.MenuItem.new_with_label(workspace.get_name())
                if workspace != window.get_workspace():
                    item.connect(
                        "activate", self.__move_to_workspace, workspace
                    )
                else:
                    item.set_sensitive(False)
                submenu.append(item)

        if has_kill:
            self.append(Gtk.SeparatorMenuItem())
            app = window.get_application()
            pid = app.get_pid()
            item = Gtk.MenuItem.new_with_label(_("Force quit"))
            self.append(item)
            item.connect("activate", _kill, [pid], app.get_name())
    
        self.append(Gtk.SeparatorMenuItem())

        item = Gtk.MenuItem.new_with_label(_("Close"))
        item.connect(
            "activate", lambda item: window.close(Gtk.get_current_event_time())
        )
        self.append(item)

    def __move_to_workspace(self, menu_item, workspace):
        self.__window.move_to_workspace(workspace)
    
    def __minimize(self, menu_item):
        self.__window.unshade()
        self.__window.minimize()


class WindowMenu(Gtk.Menu):
    """The menu for a list of windows."""

    def __init__(self, window_items, screen, group_name, has_kill=False):
        """
        Initialize a WindowMenu.

        @param window_items: A list of C{WindowItem}s.
        @param screen: The C{Wnck.Screen}.
        @param group_name: The name of the windows' group.
        @param has_kill: If C{True}, the menu contains a "kill" menu entry
            which kills the process the windows belong to. If the windows
            belong to different processes, each submenu has its own "kill"
            menu entry.
        """
        Gtk.Menu.__init__(self)
        self.__group_name = group_name
        self.__window_items = window_items
        window_items.sort(key=lambda item: item.get_name())
        time = Gtk.get_current_event_time()
        has_minimized_windows = False
        has_unminimized_windows = False
        same_app = True
        self.__pids = []
        for window_item in window_items:
            pid = window_item.window.get_pid()
            if pid == 0 or pid in self.__pids:
                continue
            self.__pids.append(pid)
        for window_item in window_items:
            if window_item.window.is_minimized():
                has_minimized_windows = True
            else:
                has_unminimized_windows = True
            self.append(render_menu_item(window_item, has_submenu=True))
        self.append(Gtk.SeparatorMenuItem())
        item = Gtk.MenuItem.new_with_label(_("Show all"))
        item.connect("activate", self.__restore_all)
        item.set_sensitive(has_minimized_windows)
        self.append(item)
        item = Gtk.MenuItem.new_with_label(_("Hide all"))
        item.connect("activate", self.__minimize_all)
        item.set_sensitive(has_unminimized_windows)
        self.append(item)
        if has_kill:
            self.append(Gtk.SeparatorMenuItem())
            item = Gtk.MenuItem.new_with_label(_("Force quit"))
            item.connect("activate", _kill, self.__pids, group_name)
            self.append(item)
        self.append(Gtk.SeparatorMenuItem())
        item = Gtk.MenuItem.new_with_label(_("Close all"))
        item.connect("activate", self.__close_all)
        self.append(item)

    def __minimize_all(self, menu_item):
        for window_item in self.__window_items:
            window_item.window.minimize()

    def __restore_all(self, menu_item):
        for window_item in self.__window_items:
            if window_item.window.is_minimized():
                window_item.window.unminimize(Gtk.get_current_event_time())

    def __close_all(self, menu_item):
        n_windows = len(self.__window_items)
        if n_windows == 0:
            rox.info(
                _("%s hasn't got any open windows anymore.") %
                self.__group_name
            )
            return
        if not rox.confirm(
                _("Close all %d windows of %s?") %
                (n_windows, self.__group_name),
                Gtk.STOCK_CLOSE, _("Close all")):
            return
        for window_item in self.__window_items:
            window_item.window.close(Gtk.get_current_event_time())
