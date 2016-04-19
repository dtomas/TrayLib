from rox import tasks

from traylib.tray import Tray


class ManagedTray(Tray):

    def __init__(self, managers):
        """
        Initialize the managed tray.

        @param icon_config: The L{IconConfig}.
        @param tray_config: The L{TrayConfig}.
        @param managers: List of callables, to be called with the tray as
            their argument and returning a tuple of generator functions
            to manage and unmanage the tray.
        """
        Tray.__init__(self)
        self.__managers = [manager(self) for manager in managers]
        self.__blocked = False

        def _manage():
            while self.__blocked:
                yield None
            self.__blocked = True
            for manage, _unmanage in self.__managers:
                m = manage()
                if m is not None:
                    for x in m:
                        yield None
            self.__blocked = False
        tasks.Task(_manage())

    def destroy(self):
        """Clean up the tray. Calls all unmanage functions."""
        def _unmanage():
            while self.__blocked:
                yield None
            self.__blocked = True
            for _manage, unmanage in self.__managers:
                um = unmanage()
                if um is not None:
                    for x in um:
                        yield None
            self.__blocked = False
            Tray.destroy(self)
        tasks.Task(_unmanage())

    def refresh(self):
        """Refresh the tray by calling unmanage and manage functions."""
        def _refresh():
            while self.__blocked:
                yield None
            self.__blocked = True
            for manage, unmanage in self.__managers:
                um = unmanage()
                if um is not None:
                    for x in um:
                        yield None
                m = manage()
                if m is not None:
                    for x in m:
                        yield None
            self.__blocked = False
        tasks.Task(_refresh())
