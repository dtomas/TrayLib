from rox import applet
from rox.applet import Applet

from traylib import *
from traylib.tray_container import TrayContainer


class TrayApplet(Applet, TrayContainer):
    """
    An applet showing a L{Tray}.
    """
    
    def __init__(self, xid, min_size, max_size, tray_class, icon_config, 
                tray_config, *tray_args):
        """
        Creates a new TrayApplet.
        
        @param xid: The XID of a gtk.Socket widget.
        """
        Applet.__init__(self, xid)
        orientation = self.get_panel_orientation()
        if orientation == 'Top':
            edge = TOP
        elif orientation == 'Bottom':
            edge = BOTTOM
        elif orientation == 'Left':
            edge = LEFT
        elif orientation == 'Right':
            edge = RIGHT
        else:
	    edge = 0
        icon_config.edge = edge
        icon_config.pos_func = self.position_menu
        vertical = orientation in ('Left', 'Right')
        if vertical:
            self.set_size_request(8, -1)
        else:
            self.set_size_request(-1, 8)
        TrayContainer.__init__(self, min_size, max_size, vertical, tray_class, 
                                icon_config, tray_config, *tray_args)

    def get_icon_size(self):
        """
        @return: 0.75 times the width (if vertical) or height of the panel. 
        """
        size = TrayContainer.get_icon_size(self)
        size *= 0.75
        size -= 2
        return int(size)

    def get_panel_orientation(self):
        """@return: The panel orientation ('Top', 'Bottom', 'Left', 'Right')"""
        pos = self.socket.property_get('_ROX_PANEL_MENU_POS', 'STRING', False)
        if pos: pos = pos[2]
        if pos:
            side = pos.split(',')[0]
        else:
            side = None
        return side
