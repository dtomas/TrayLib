import os

import rox
from rox.options import Option

from traylib import LEFT, RIGHT, TOP, BOTTOM, ICON_THEME
from traylib.tray_window import TrayWindow
from traylib.tray_applet import TrayApplet
from traylib.icon_config import IconConfig
from traylib.tray_config import TrayConfig


class Main(object):
    
    def __init__(self, name):
        """Creates a new C{Main} object."""
        
        self.name = name

        self.init_options()
        rox.app_options.notify()
        
        self.init_config()

    def init_options(self):
        self.__o_icon_size_min = Option("icon_size_min", 16)
        self.__o_icon_size_max = Option("icon_size_max", 32)
        self.__o_effects = Option("effects", True)
        self.__o_separator_left = Option("separator_left", False)
        self.__o_separator_right = Option("separator_right", False)
        self.__o_menus = Option("menus", RIGHT)
        self.__o_hidden = Option("hidden", False)
        
    def init_config(self):
        separators = 0
        if self.__o_separator_left.int_value:
            separators |= LEFT
        if self.__o_separator_right.int_value:
            separators |= RIGHT
        self.__icon_config = IconConfig(
            size=16,
            edge=0,
            effects=self.__o_effects.int_value, 
            pos_func=None, 
            hidden=self.__o_hidden.int_value
        )
        self.__tray_config = TrayConfig(
            name=self.name,
            menus=self.__o_menus.int_value,
            separators=separators,
        )

    def mainloop(self, app_args, tray_class, *tray_args):
        """
        Starts the main loop and returns when the tray app is quit.
        
        @param app_args: The arguments passed to the app.
        @param tray_class: The type of tray. Must be a subclass of L{Tray}.
        @param *tray_args: Additional args for the L{Tray} subclass.
        """
        ICON_THEME.append_search_path(os.path.join(rox.app_dir, 'icons'))
        rox.app_options.add_notify(self.options_changed)
        if len(app_args) >= 2:
            self.__main_window = TrayApplet(app_args[1],
                                            self.__o_icon_size_min.int_value,
                                            self.__o_icon_size_max.int_value,
                                            tray_class, 
                                            self.__icon_config,
                                            self.__tray_config,
                                            *tray_args)
        else:
            self.__main_window = TrayWindow(self.__o_icon_size_min.int_value,
                                            self.__o_icon_size_max.int_value,
                                            tray_class, 
                                            self.__icon_config, 
                                            self.__tray_config, 
                                            *tray_args)
        self.__main_window.show()
        rox.mainloop()

    def options_changed(self):
        """Called when the options have changed."""
        if (self.__o_icon_size_min.has_changed or
                self.__o_icon_size_max.has_changed):
            self.__main_window.update_icon_size(
                self.__o_icon_size_min.int_value,
                self.__o_icon_size_max.int_value)
    
        if (self.__o_separator_left.has_changed or
                self.__o_separator_right.has_changed):
            separators = 0
            if self.__o_separator_left.int_value:
                separators |= LEFT
            if self.__o_separator_right.int_value:
                separators |= RIGHT
            self.__tray_config.separators = separators

        if self.__o_menus.has_changed:
            self.__tray_config.menus = self.__o_menus.int_value

        if self.__o_effects.has_changed:
            self.__icon_config.effects = self.__o_effects.int_value

    icon_config = property(lambda self : self.__icon_config)
    tray_config = property(lambda self : self.__tray_config)
    tray = property(lambda self : self.__main_window.tray if self.__main_window
                                  else None)
