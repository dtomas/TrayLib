from rox import tasks

from traylib.tray import Tray
from traylib.menu_icon import MenuIcon


class ManagedTray(Tray):

    def __init__(self, icon_config, tray_config, create_manager,
                 menu_icon_class=MenuIcon, *menu_icon_args):
        Tray.__init__(self, icon_config, tray_config, menu_icon_class,
                      *menu_icon_args)
        self.__manager = create_manager(self)
        tasks.Task(self.__manager.init())

    def add_icon(self, box_id, icon_id, icon):
        Tray.add_icon(self, box_id, icon_id, icon)
        self.__manager.icon_added(icon)

    def remove_icon(self, icon_id):
        Tray.remove_icon(self, icon_id, icon)
        self.__manager.icon_removed(icon)

    def quit(self):
        tasks.Task(self.__manager.quit())
