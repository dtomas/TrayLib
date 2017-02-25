import gobject
import gtk

from traylib import ICON_THEME


class IIconLoader(object):
    """Interface for icon loaders."""

    def get_pixbuf(self, size):
        """@return: a gtk.gdk.Pixbuf of the given size."""
        raise NotImplementedError

    def get_path(self, size):
        """@return: the path of the icon or None."""


class ThemedIcon(IIconLoader):
    """Loads themed icons."""

    def __init__(self, icon_name):
        """
        Initialize ThemedIcon.

        @param icon_name: The name of the icon.
        """
        self.icon_name = icon_name
        """The name of the icon."""

    def get_pixbuf(self, size):
        icon_info = ICON_THEME.lookup_icon(self.icon_name, size, 0)
        if not icon_info:
            return None
        icon_path = icon_info.get_filename()
        try:
            return gtk.gdk.pixbuf_new_from_file(icon_path)
        except gobject.GError:
            return None

    def get_path(self, size):
        icon_info = ICON_THEME.lookup_icon(self.icon_name, size, 0)
        if not icon_info:
            return None
        return icon_info.get_filename()


class PixbufIcon(IIconLoader):
    """Wraps an already existing gtk.gdk.Pixbuf."""

    def __init__(self, pixbuf):
        """
        Initialize PixbufIcon.

        @param pixbuf: The gtk.gdk.Pixbuf get_pixbuf() will return.
        """
        self.pixbuf = pixbuf

    def get_pixbuf(self, size):
        return self.pixbuf

    def get_path(self, size):
        return None


class FileIcon(IIconLoader):
    """Loads an icon from a path."""

    def __init__(self, path):
        """
        Initialize FileIcon.

        @param path: The path to load the icon from.
        """
        self.path = path

    def get_pixbuf(self, size):
        try:
            return gtk.gdk.pixbuf_new_from_file(self.path)
        except gobject.GError:
            return None

    def get_path(self, size):
        return self.path
