from rox import tasks

from traylib.tray import Tray
from traylib.menu_icon import MenuIcon


class ManagedTray(Tray):

    def __init__(self, icon_config, tray_config, managers,
                 create_menu_icon=MenuIcon):
        Tray.__init__(self, icon_config, tray_config, create_menu_icon)
        self.__managers = [manager(self) for manager in managers]
        self.__blocked = False

        def _manage():
            while self.__blocked:
                yield None
            self.__blocked = True
            for manage, _unmanage in self.__managers:
                for x in manage():
                    yield None
            self.__blocked = False
        tasks.Task(_manage())

    def quit(self):
        def _unmanage():
            while self.__blocked:
                yield None
            self.__blocked = True
            for _manage, unmanage in self.__managers:
                for x in unmanage():
                    yield None
            self.__blocked = False
        tasks.Task(_unmanage())

    def refresh(self):
        def _refresh():
            while self.__blocked:
                yield None
            self.__blocked = True
            for manage, unmanage in self.__managers:
                for x in unmanage():
                    yield None
                for x in manage():
                    yield None
            self.__blocked = False
        tasks.Task(_refresh())
