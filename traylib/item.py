from gi.repository import GObject, Gdk

from traylib import ICON_THEME, pixbuf_helper


class Item(GObject.Object):

    def __init__(self):
        GObject.Object.__init__(self)
        self.__icon_theme_changed_handler = ICON_THEME.connect(
            "changed", self.__theme_changed
        )
        self.__is_destroyed = False

    def changed(self, *props):
        self.emit("changed", set(props))

    def destroy(self):
        if self.__is_destroyed:
            return
        self.__is_destroyed = True
        ICON_THEME.disconnect(self.__icon_theme_changed_handler)
        self.emit("destroyed")

    def __theme_changed(self, icon_theme):
        self.changed("icon")

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

    def is_minimized(self):
        return False

    def is_active(self):
        return False

    def get_name(self):
        """
        Override this to determine the name.

        @return: The new name.
        """
        return ""

    def get_icon(self, size):
        """
        This determines the C{GdkPixbuf.Pixbuf} the C{Item} should have.

        This method tries to use the L{IIconLoader}s returned by
        L{Item.get_icons} to load the pixbuf.

        @return: The new pixbuf.
        """
        for icon in self.get_icons():
            pixbuf = icon.get_pixbuf(size)
            if pixbuf is not None:
                return pixbuf_helper.scale_pixbuf_to_size(pixbuf, size)
        return None

    def find_icon_name(self):
        for icon in self.get_icons():
            if hasattr(icon, "icon_name"):
                icon_info = ICON_THEME.lookup_icon(icon.icon_name, 48, 0)
                if icon_info is not None:
                    return icon.icon_name
        return ""

    def find_icon_path(self):
        for icon in self.get_icons():
            path = icon.get_path(48)
            if path is not None:
                return path
        return None

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

    def mouse_wheel_up(self, time=0):
        """
        Override this to determine the action when the mouse wheel is scrolled
        up.

        @param time: The time of the scroll event.
        """
        return False

    def mouse_wheel_down(self, time=0):
        """
        Override this to determine the action when the mouse wheel is scrolled
        down.

        @param time: The time of the scroll event.
        """
        return False

    def spring_open(self, time=0):
        """
        Override this to determine the action when the mouse pointer stays on
        an icon some time while dragging.

        @return: C{True} if C{spring_open()} should be called again in a
            second.
        """
        return False

    def click(self, time=0):
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
        @param action: One of C{Gdk.DragAction.COPY}, C{Gdk.DragAction.MOVE}
            or C{Gdk.DragAction.LINK}.
        """
        pass

    def get_drag_source_targets(self):
        return []

    def get_drag_source_actions(self):
        return Gdk.DragAction.DEFAULT

    def drag_data_get(self, context, data, info, time):
        pass


GObject.type_register(Item)
GObject.signal_new(
    "changed", Item, GObject.SignalFlags.RUN_FIRST,
    GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)
)
GObject.signal_new(
    "destroyed", Item, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()
)
