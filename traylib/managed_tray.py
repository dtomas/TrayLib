from rox import tasks

from traylib.tray import Tray
from traylib.menu_icon import MenuIcon


class ManagedTray(Tray):

    def __init__(self, icon_config, tray_config, managers,
                 create_menu_icon=MenuIcon):
        Tray.__init__(self, icon_config, tray_config, create_menu_icon)
        self.__managers = [manager(self) for manager in managers]

        for manage, _unmanage in self.__managers:
            tasks.Task(manage())

    def quit(self):
        for _manage, unmanage in self.__managers:
            tasks.Task(unmanage())
