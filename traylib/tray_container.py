

class TrayContainer(object):
    """
    An object containing a L{Tray}. If you subclass this, you must also
    subclass C{gtk.Container}.
    """

    def __init__(self, min_size, max_size, vertical, tray, render_tray,
                 icon_config, tray_config):
        """
        Initialize a C{TrayContainer}.

        @param min_size: The minimum size of the icons.
        @param max_size: The maximum size of the icons.
        @param vertical: C{True} if the tray should be vertical.
        @param create_tray: Callable to create the tray from an
            L{IconConfig} and a L{TrayConfig}.
        @param icon_config: The L{IconConfig}.
        @param tray_config: The L{TrayConfig}.
        """
        self.__render_tray = render_tray
        self.__icon_config = icon_config
        self.__tray_config = tray_config
        self.__size = 0
        self.__max_size = max_size
        self.__min_size = min_size
        self.__vertical = vertical
        self.__tray = tray
        tray_widget = self.__render_tray(self.__tray)
        tray_widget.connect("destroy", self.__tray_widget_destroyed)
        self.add(tray_widget)
        self.set_name(tray_config.name + "PanelApplet")
        self.connect('size-allocate', self.__size_allocate)

    def __tray_widget_destroyed(self, widget):
        self.destroy()

    def __size_allocate(self, widget, rectangle):
        if self.__vertical:
            size = rectangle.width
        else:
            size = rectangle.height
        if size == self.__size:
            return
        self.__size = size
        self.update_icon_size(self.__min_size, self.__max_size)

    def update_icon_size(self, min_size, max_size):
        """
        Update the size of the tray's icons and set the maximum icon size.

        @param min_size: The minimum icon size.
        @param max_size: The maximum icon size.
        """
        self.__max_size = max_size
        self.__min_size = min_size
        size = self.get_icon_size()
        self.__icon_config.size = max(min_size, min(size, max_size))
        if self.__vertical:
            self.set_size_request(int(self.__min_size * 1.5), -1)
        else:
            self.set_size_request(-1, int(self.__min_size * 1.5))

    def get_icon_size(self):
        """
        Extend this to determine the maximum icon size.

        @return: The maximum icon size.
        """
        return self.__size

    is_vertical = property(lambda self: self.__vertical)
    """C{True} if the container is vertical."""

    tray = property(lambda self: self.__tray)
    """The container's L{Tray}."""
