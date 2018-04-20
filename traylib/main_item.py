import os

from gi.repository import Gtk

import rox
from rox import filer, InfoWin

from traylib import _
from traylib.item import Item


class MainItem(Item):
    """The main item of a L{Tray}."""

    def __init__(self, tray, tray_config, icon_config):
        """
        Initialize MainItem.

        @param tray: The item's L{Tray}.
        @param tray_config: The tray's configuration.
        @param icon_config: The configuration of the tray's icons.
        """
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
        """Show information."""
        InfoWin.infowin(self.__tray_config.name)

    def __show_help(self, menu_item=None):
        """Show help."""
        filer.open_dir(os.path.join(rox.app_dir, 'Help'))

    def __show_options(self, menu_item=None):
        """Show the options."""
        if self.__icon_config.vertical:
            options_xml = 'OptionsV.xml'
        else:
            options_xml = 'OptionsH.xml'
        rox.edit_options(os.path.join(rox.app_dir, options_xml))

    def __quit(self, menu_item=None):
        """Quit the Tray."""
        if rox.confirm(
                _("Really quit %s?") % self.__tray_config.name,
                Gtk.STOCK_QUIT):
            self.__tray.destroy()

    def __toggle_lock_icons(self, menu_item):
        self.__icon_config.locked = not self.__icon_config.locked

    def get_menu_right(self):
        menu = Gtk.Menu()
        item = Gtk.MenuItem.new_with_label(_("Help"))
        item.connect("activate", self.__show_help)
        menu.add(item)
        item = Gtk.MenuItem.new_with_label(_("Information"))
        item.connect("activate", self.__show_info)
        menu.add(item)
        menu.add(Gtk.SeparatorMenuItem())
        custom_menu_items = self.get_custom_menu_items()
        for item in custom_menu_items:
            menu.add(item)
        if custom_menu_items:
            menu.add(Gtk.SeparatorMenuItem())
        item = Gtk.MenuItem.new_with_label(_("Preferences"))
        item.connect("activate", self.__show_options)
        menu.add(item)
        menu.add(Gtk.SeparatorMenuItem())
        item = Gtk.CheckMenuItem.new_with_label(_("Lock icons"))
        item.set_active(self.__icon_config.locked)
        item.connect("toggled", self.__toggle_lock_icons)
        menu.add(item)
        menu.add(Gtk.SeparatorMenuItem())
        item = Gtk.MenuItem.new_with_label(_("Quit"))
        item.connect("activate", self.__quit)
        menu.add(item)
        menu.show_all()
        return menu

    tray = property(lambda self: self.__tray)

    # Methods which may be overridden by subclasses:

    def get_custom_menu_items(self):
        """Override this to return custom items for the main menu."""
        return []
