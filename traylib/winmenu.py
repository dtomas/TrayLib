import os
import struct
from urllib import pathname2url

import gtk
import rox

from traylib import (
    ICON_THEME, TARGET_WNCK_WINDOW_ID, TARGET_URI_LIST, wnck, _
)
from traylib.menu_renderer import render_menu_item
from traylib.pixbuf_helper import scale_pixbuf_to_size


def _kill(menu_item, pids, name):
    if rox.confirm(
            _("Really force %s to quit?") % name,
            gtk.STOCK_QUIT, _("Force quit")):
        for pid in pids:
            rox.processes.PipeThroughCommand(
                ('kill', '-KILL', str(pid)), None, None
            ).wait()


def get_filer_window_path(window):
    name = window.get_name()
    if (window.get_class_group().get_name() != 'ROX-Filer' or
            not (name.startswith('/') or name.startswith('~'))):
        return ''
    for i in range(1-len(name), 0):
        if name[-i] == '(' or name[-i] == '+':
            name = name[:-(i+1)]
            break
    return name


class WindowActionMenu(gtk.Menu):
    """
    A menu that shows actions for a C{wnck.Window}.
    """

    def __init__(self, window, has_kill=False, path=None, parent=None):
        """
        Creates a new C{WindowActionMenu}.
        
        @param has_kill: If C{True}, the menu contains an entry to kill the 
            process the window belongs to.
        @param path: If not C{None}, indicates that the window is a filemanager
            window showing the directory C{path}.
        @param parent: The L{WindowMenu} showing all directories.
        """
        gtk.Menu.__init__(self)
    
        self.__window = window
        screen = window.get_screen()
        if path:
            self.__path = os.path.expanduser(path)
        else:
            self.__path = None
        self.__parent = parent
    
        item = gtk.ImageMenuItem(_("Activate"))
        item.get_image().set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_MENU)
        item.connect("activate", self.__winaction2, wnck.Window.activate)
        self.append(item)
    
        self.append(gtk.SeparatorMenuItem())

        actions = window.get_actions()        

        if window.is_maximized():
            item = gtk.ImageMenuItem(_("Unmaximize"))
            item.get_image().set_from_stock(
                gtk.STOCK_ZOOM_OUT, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", self.__winaction, wnck.Window.unmaximize)
            item.set_sensitive(wnck.WINDOW_ACTION_UNMAXIMIZE & actions)
        else:
            item = gtk.ImageMenuItem(_("Maximize"))
            item.get_image().set_from_stock(
                gtk.STOCK_ZOOM_100, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", self.__winaction, wnck.Window.maximize)
            item.set_sensitive(wnck.WINDOW_ACTION_MAXIMIZE & actions)
        self.append(item)
    
        if window.is_minimized():
            item = gtk.ImageMenuItem(_("Show"))
            item.get_image().set_from_stock(gtk.STOCK_REDO, gtk.ICON_SIZE_MENU)
            item.connect("activate", self.__winaction2, wnck.Window.unminimize)
        else:
            item = gtk.ImageMenuItem(_("Hide"))
            item.get_image().set_from_stock(gtk.STOCK_UNDO, gtk.ICON_SIZE_MENU)
            item.connect("activate", self.__minimize)
        self.append(item)
    
        if window.is_shaded():
            item = gtk.ImageMenuItem(_("Unshade"))
            item.get_image().set_from_stock(
                gtk.STOCK_GOTO_BOTTOM, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", self.__winaction, wnck.Window.unshade)
            item.set_sensitive(wnck.WINDOW_ACTION_UNSHADE & actions)
        else:
            item = gtk.ImageMenuItem(_("Shade"))
            item.get_image().set_from_stock(
                gtk.STOCK_GOTO_TOP, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", self.__winaction, wnck.Window.shade)
            item.set_sensitive(wnck.WINDOW_ACTION_SHADE & actions)
        self.append(item)
    
        self.append(gtk.SeparatorMenuItem())
    
        if window.is_pinned() or window.is_sticky():
            item = gtk.ImageMenuItem(_("Only on this workspace"))
            item.get_image().set_from_stock(
                gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", self.__winaction, wnck.Window.unstick)
            item.connect("activate", self.__winaction, wnck.Window.unpin)
            item.set_sensitive(wnck.WINDOW_ACTION_UNSTICK & actions)
        else:
            item = gtk.ImageMenuItem(_("Always on visible workspace"))
            item.get_image().set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
            item.connect("activate", self.__winaction, wnck.Window.stick)
            item.connect("activate", self.__winaction, wnck.Window.pin)
            item.set_sensitive(wnck.WINDOW_ACTION_STICK & actions)
        self.append(item)
    
        if screen.get_workspace_count() > 1:
            item = gtk.ImageMenuItem(_("Move to workspace"))
            item.get_image().set_from_stock(
                gtk.STOCK_JUMP_TO, gtk.ICON_SIZE_MENU
            )
            self.append(item)
            submenu = gtk.Menu()
            item.set_submenu(submenu)
            for i in range(0, screen.get_workspace_count()):
                workspace = screen.get_workspace(i)
                item = gtk.MenuItem(workspace.get_name())
                if workspace != window.get_workspace():
                    item.connect(
                        "activate", self.__move_to_workspace, workspace
                    )
                else:
                    item.set_sensitive(False)
                submenu.append(item)

        if has_kill:
            self.append(gtk.SeparatorMenuItem())
            app = window.get_application()
            pid = app.get_pid()
            item = gtk.ImageMenuItem(_("Force quit"))
            item.get_image().set_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU)
            self.append(item)
            item.connect("activate", _kill, [pid], app.get_name())
    
        self.append(gtk.SeparatorMenuItem())

        if self.__parent and self.__path and os.path.isdir(self.__path):
            item = gtk.ImageMenuItem(_("Close subdirectories"))
            item.get_image().set_from_stock(
                gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", self.__close_subdirs)
            self.append(item)

        item = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
        item.connect("activate", self.__winaction2, wnck.Window.close)
        self.append(item)

    def __close_subdirs(self, menu_item):
        path = self.__path + os.sep
        windows = []
        for window in self.__parent.get_windows():
            window_path = os.path.expanduser(get_filer_window_path(window))
            if window_path and window_path.startswith(path):
                windows.append(window)
        if not windows:
            rox.info(_("There are no windows showing subdirectories of %s") 
                        % self.__path)
        n_windows = len(windows)
        if n_windows > 1:
            if not rox.confirm(
                    _("Close all %d subdirectories of %s?") %
                    (n_windows, self.__path), gtk.STOCK_CLOSE):
                return
        for window in windows:
            window.close(gtk.get_current_event_time())
            
    def __winaction(self, menu_item, func):
        func(self.__window)
    
    def __winaction2(self, menu_item, func):
        func(self.__window, gtk.get_current_event_time())
    
    def __move_to_workspace(self, menu_item, workspace):
        self.__window.move_to_workspace(workspace)
    
    def __minimize(self, menu_item):
        self.__window.unshade()
        self.__window.minimize()


class WindowMenu(gtk.Menu):
    """
    The menu for a list of windows.
    """

    def __init__(self, window_items, screen, group_name,
                    root=None, root_icon=None, has_kill=False):
        """
        Creates a new WindowMenu.
        
        @param window_items: A list of C{WindowItem}s.
        @param root: If not C{None}, indicates that the windows are
            filemanager windows and the path prefix "root" should not be
            omitted.
        @param root_icon: The icon to show for the root menu entry. This is the
            menu entry showing C{root}.
        @param has_kill: If C{True} and C{type==TYPE_OPTIONS}, the menu
            contains a "kill" menu entry which kills the process the windows
            belong to. If the windows belong to different processes, each
            submenu has its own "kill" menu entry.
        """
        gtk.Menu.__init__(self)
        self.__group_name = group_name
        self.__window_items = window_items
        window_items.sort(key=lambda item: item.get_name())
        time = gtk.get_current_event_time()
        self.__active_window = screen.get_active_window()
        has_minimized_windows = False
        has_unminimized_windows = False
        same_app = True
        self.__pids = []
        for window_item in window_items:
            pid = window_item.window.get_application().get_pid()
            if pid in self.__pids:
                continue
            self.__pids.append(pid)
        for window_item in window_items:
            if window_item.window.is_minimized():
                has_minimized_windows = True
            else:
                has_unminimized_windows = True
            item = render_menu_item(window_item, has_submenu=True)#WindowMenuItem(window, icon, root, root_icon)
            item.set_submenu(
                WindowActionMenu(
                    window_item.window, has_kill and len(self.__pids) > 1,
                    window_item.root_path, self
                )
            )
            self.append(item)
        self.append(gtk.SeparatorMenuItem())
        item = gtk.ImageMenuItem(_("Show all"))
        item.get_image().set_from_stock(gtk.STOCK_REDO, gtk.ICON_SIZE_MENU)
        item.connect("activate", self.__restore_all)
        item.set_sensitive(has_minimized_windows)
        self.append(item)
        item = gtk.ImageMenuItem(_("Hide all"))
        item.get_image().set_from_stock(gtk.STOCK_UNDO, gtk.ICON_SIZE_MENU)
        item.connect("activate", self.__minimize_all)
        item.set_sensitive(has_unminimized_windows)
        self.append(item)
        if has_kill:
            self.append(gtk.SeparatorMenuItem())
            item = gtk.ImageMenuItem(_("Force quit"))
            item.get_image().set_from_stock(
                gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU
            )
            item.connect("activate", _kill, self.__pids, group_name)
            self.append(item)
        self.append(gtk.SeparatorMenuItem())
        item = gtk.ImageMenuItem(_("Close all"))
        item.get_image().set_from_stock(
            gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU
        )
        item.connect("activate", self.__close_all)
        self.append(item)

    def __minimize_all(self, menu_item):
        for window_item in self.__window_items:
            window_item.window.minimize()

    def __restore_all(self, menu_item):
        for window_item in self.__window_items:
            if window_item.window.is_minimized():
                window_item.window.unminimize(gtk.get_current_event_time())

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
                gtk.STOCK_CLOSE, _("Close all")):
            return
        for window_item in self.__window_items:
            window_item.window.close(gtk.get_current_event_time())
