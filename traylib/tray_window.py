from rox import Window

from traylib import *
from traylib.tray_container import TrayContainer 


class TrayWindow(Window, TrayContainer):
    """
    A window showing a L{Tray}.
    """
    
    def __init__(self, min_size, max_size, tray_class, icon_config, 
                tray_config, *tray_args):
        """
        Creates a new C{TrayWindow}.
        """
        Window.__init__(self)
        self.set_size_request(-1, 48)
        TrayContainer.__init__(self, min_size, max_size, False, tray_class, 
                                icon_config, tray_config, *tray_args)

    def get_icon_size(self):
        """
        @return: Half the height of the window.
        """
        size = TrayContainer.get_icon_size(self)
        size *= 0.5
        return int(size)
