import gtk
import gobject

from traylib import ICON_THEME


class Item(gobject.GObject):

    def __init__(self):
        gobject.GObject.__init__(self)
        self.__icon_theme_changed_handler = ICON_THEME.connect(
            "changed", self.__theme_changed
        )
        self.__is_destroyed = False

    def destroy(self):
        if self.__is_destroyed:
            return
        self.__is_destroyed = True
        ICON_THEME.disconnect(self.__icon_theme_changed_handler)
        self.emit("destroyed")

    def __theme_changed(self, icon_theme):
        self.emit("icon-changed")

    def is_visible(self):
        """
        Override this to determine the visibility.
        
        @return: C{True} if the C{Item} should be visible.
        """
        return True

    def is_greyed_out(self):
        return False

    def is_blinking(self):
        return False

    def is_arrow_blinking(self):
        return False

    def get_name(self):
        """
        Override this to determine the name.
        
        @return: The new name.
        """
        return ""

    def get_icon(self, size):
        """
        This determines the C{gtk.gdk.Pixbuf} the C{Item} should have.

        This method tries to use the L{IIconLoader}s returned by
        L{Item.get_icons} to load the pixbuf.

        @return: The new pixbuf.
        """
        for icon in self.get_icons():
            pixbuf = icon.get_pixbuf(size)
            if pixbuf is not None:
                return pixbuf
        return None

    def find_icon_name(self):
        for icon in self.get_icons():
            if hasattr(icon, "icon_name"):
                icon_info = ICON_THEME.lookup_icon(icon.icon_name, 48, 0)
                if icon_info is not None:
                    return icon.icon_name
        return ""

    def get_icons(self):
        """
        Override this to determine the icons that C{Item.get_icon} should try.

        @return: The list of L{IIconLoader}s.
        """
        return []

    def get_emblem(self):
        """
        Override this to determine the emblem to be shown in the upper left 
        corner.
        
        @return: The new emblem.
        """
        return None

    def get_zoom(self):
        """
        Extend this to determine the zoom factor.
        
        @return: The new zoom factor.
        """
        return 1.0

    def has_arrow(self):
        """
        Override this to determine whether the C{Icon} has an arrow or not.
        
        @return: C{True} if the C{Icon} should have an arrow.
        """
        return False

    def get_menu_left(self):
        """
        Override this to determine the menu that pops up when left-clicking the
        C{Icon}. (In case the C{click()} method returned C{False}.)

        @return: The menu that pops up when left-clicking the C{Icon}.
        """
        return None

    def get_menu_right(self):
        """
        Override this to determine the menu that pops up when right-clicking
        the C{Icon}.

        @return: The menu that pops up when right-clicking the C{Icon}.
        """
        return None

    def mouse_wheel_up(self, time=0L):
        """
        Override this to determine the action when the mouse wheel is scrolled 
        up.
        
        @param time: The time of the scroll event.
        """
        return False

    def mouse_wheel_down(self, time=0L):
        """
        Override this to determine the action when the mouse wheel is scrolled 
        down.
        
        @param time: The time of the scroll event.
        """
        return False

    def spring_open(self, time=0L):
        """
        Override this to determine the action when the mouse pointer stays on
        an icon some time while dragging.
        
        @return: C{True} if C{spring_open()} should be called again in a
            second. 
        """
        return False

    def click(self, time=0L):
        """
        Override this to determine the action when left-clicking the C{Icon}. 
        If an action was performed, return C{True}, else return C{False}.
        
        @param time: The time of the click event.
        """
        return False

    def is_drop_target(self):
        return False

    def uris_dropped(self, uri_list, action):
        """
        Override this to react to URIs being dropped on the C{Icon}.
        
        @param uris: A list of URIs.
        @param action: One of C{gtk.gdk.ACTION_COPY}, C{gtk.gdk.ACTION_MOVE}
            or C{gtk.gdk.ACTION_LINK}.
        """
        pass

    def get_drag_source_targets(self):
        return []

    def get_drag_source_actions(self):
        return 0

    def drag_data_get(self, context, data, info, time):
        pass


gobject.type_register(Item)
gobject.signal_new(
    "is-visible-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "is-blinking-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    ()
)
gobject.signal_new(
    "is-arrow-blinking-changed", Item, gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "is-greyed-out-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    ()
)
gobject.signal_new(
    "name-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "icon-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "emblem-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "zoom-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "has-arrow-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "menu-left-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "menu-right-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "drag-source-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    ()
)
gobject.signal_new(
    "is-drop-target-changed", Item, gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "destroyed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
