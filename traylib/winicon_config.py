from traylib import *
from traylib.config import Config


class WinIconConfig(Config):

    def __init__(self, all_workspaces, arrow):
        """
        Creates a new C{WinIconConfig}.
        
        @param all_workspaces: If C{True}, windows on all workspaces should be
            visible in the L{WinIcon}'s menu.
        @param arrow: If C{True}, the L{WinIcon}s associated with the 
            C{WinIconConfig} have an arrow on them when they have more than one
            visible window.
        """
        
        Config.__init__(self)
        
        self.add_attribute('all_workspaces', all_workspaces,
                           'update_option_all_workspaces')
        self.add_attribute('arrow', arrow, 'update_option_arrow')


    all_workspaces = property(lambda self : self.get_attribute(
                                                'all_workspaces'),
                              lambda self, all_workspaces : (
                                  self.set_attribute('all_workspaces',
                                                     all_workspaces)))
    """
    C{True}, if windows on all workspaces should be visible in the associated
    L{WinIcon}s' menus.
    """
    
    arrow = property(lambda self : self.get_attribute('arrow'),
          lambda self, arrow : self.set_attribute('arrow', arrow))
    """
    C{True}, if the L{WinIcon}s associated with the C{WinIconConfig} should
    have an arrow on them when they have more than one visible window.
    """
