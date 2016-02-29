import os

import gtk
import rox
from rox import filer, InfoWin

from traylib.item import Item


class MainItem(Item):

    def __init__(self, tray, tray_config, icon_config):
        Item.__init__(self)
        self.__tray = tray
        self.__tray_config = tray_config
        self.__icon_config = icon_config

    def click(self, time):
        self.__icon_config.hidden = not self.icon_config.hidden

    def mouse_wheel_up(self, time):
        self.__icon_config.hidden = False

    def mouse_wheel_down(self, time):
        self.__icon_config.hidden = True

    def __show_info(self, menu_item=None):
        """Shows information."""
        InfoWin.infowin(self.__tray_config.name)

    def __show_help(self, menu_item=None):
        """Shows information."""
        filer.open_dir(os.path.join(rox.app_dir, 'Help'))

    def __show_options(self, menu_item=None):
        """Shows the options."""
        if self.__icon_config.vertical:
            options_xml = 'OptionsV.xml'
        else:
            options_xml = 'OptionsH.xml'
        rox.edit_options(os.path.join(rox.app_dir, options_xml))

    def __quit(self, menu_item=None):
        """Quits the Tray."""
        if rox.confirm(
                _("Really quit %s?") % self.__tray_config.name,
                gtk.STOCK_QUIT):
            self.__tray.destroy()

    def get_menu_right(self):
        menu = gtk.Menu()
        item = gtk.ImageMenuItem(gtk.STOCK_HELP)
        item.connect("activate", self.__show_help)
        menu.add(item)
        item = gtk.ImageMenuItem(gtk.STOCK_DIALOG_INFO)
        item.connect("activate", self.__show_info)
        menu.add(item)    
        menu.add(gtk.SeparatorMenuItem())
        custom_menu_items = self.get_custom_menu_items()
        for item in custom_menu_items:
            menu.add(item)
        if custom_menu_items:
            menu.add(gtk.SeparatorMenuItem())
        item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        item.connect("activate", self.__show_options)
        menu.add(item)
        menu.add(gtk.SeparatorMenuItem())
        item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        item.connect("activate", self.__quit)
        menu.add(item)
        menu.show_all()
        return menu

    tray = property(lambda self: self.__tray)


    # Methods which may be overridden by subclasses:

    def get_custom_menu_items(self):
        """Override this to return custom items for the main menu."""
        return []
