import gobject
import gtk

from traylib import ICON_THEME


class IIconLoader(object):

    def get_pixbuf(self, size):
        raise NotImplementedError


class ThemedIcon(IIconLoader):

    def __init__(self, icon_name):
        self.icon_name = icon_name

    def get_pixbuf(self, size):
        icon_info = ICON_THEME.lookup_icon(self.icon_name, size, 0)
        if not icon_info:
            return None
        icon_path = icon_info.get_filename()
        try:
            return gtk.gdk.pixbuf_new_from_file(icon_path)
        except gobject.GError:
            return None


class PixbufIcon(IIconLoader):

    def __init__(self, pixbuf):
        self.pixbuf = pixbuf

    def get_pixbuf(self, size):
        return self.pixbuf


class FileIcon(IIconLoader):

    def __init__(self, path):
        self.path = path

    def get_pixbuf(self, size):
        try:
            return gtk.gdk.pixbuf_new_from_file(self.path)
        except gobject.GError:
            return None
