from traylib import *
from traylib.config import Config


class TrayConfig(Config):
    
    def __init__(self, name, menus, separators):
        """
        Creates a new C{TrayConfig}.
        
        @param name: The name of the tray.
        @param menus: Where to show boxes for the main menu: C{LEFT}, C{RIGHT} 
            or C{LEFT|RIGHT}.
        @param separators: Where to show separators (may be C{0}).
        """
        Config.__init__(self)
        self.add_attribute('name', name, 'update_option_name')
        self.add_attribute('menus', menus, 'update_option_menus')
        self.add_attribute('separators', separators, 'update_option_separators')

    name = property(lambda self : self.get_attribute('name'),
                    lambda self, name : self.set_attribute('name', name))
    menus = property(lambda self : self.get_attribute('menus'),
                    lambda self, menus : self.set_attribute('menus', menus))
    separators = property(lambda self : self.get_attribute('separators'),
                    lambda self, separators : self.set_attribute('separators', separators))
