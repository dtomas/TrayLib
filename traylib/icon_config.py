from traylib import *
from traylib.config import Config


class IconConfig(Config):
    """
    Icon configuration object.
    """

    def __init__(self, size, edge, effects, pos_func, hidden):
        """
        Creates a new C{IconConfig}.
        
        @param size: The size of the icons.
        @param edge: The edge of the screen where the icon is. Must be one of
            0, TOP, BOTTOM, LEFT, RIGHT.
        @param pos_func: The function to call for positioning an icon's menu.
        """
        assert size > 0
        assert edge in (0, TOP, BOTTOM, LEFT, RIGHT)

        Config.__init__(self)
        self.__arrow = None

        self.add_attribute('size', size, 'update_option_size')
        self.add_attribute('edge', edge, 'update_option_edge', 'update_arrow')
        self.add_attribute('effects', effects, 'update_option_effects')
        self.add_attribute('hidden', hidden, 'update_option_hidden')
        self.add_attribute('pos_func', pos_func)

    def update_arrow(self, old_edge, edge):
        if edge == LEFT:
            pixmap = pixmaps.right
        elif edge == RIGHT:
            pixmap = pixmaps.left
        elif edge == TOP:
            pixmap = pixmaps.down
        else:
            pixmap = pixmaps.up
        self.__arrow = gtk.gdk.pixbuf_new_from_xpm_data(pixmap)            

    arrow = property(lambda self : self.__arrow)
    """The arrow pixmap."""
    
    edge = property(lambda self : self.get_attribute('edge'), 
                    lambda self, edge : self.set_attribute('edge', edge))
    """
    The edge of the screen where the icons are put. One of C{0}, C{TOP},
    C{BOTTOM}, C{LEFT}, C{RIGHT}.
    """
    
    effects = property(lambda self : self.get_attribute('effects'), 
                       lambda self, effects : self.set_attribute('effects',
                                                                 effects))
    """C{True} if effects such as smooth zooming should be shown."""
        
    pos_func = property(lambda self : self.get_attribute('pos_func'), 
                        lambda self, pos_func : self.set_attribute('pos_func',
                                                                   pos_func))
    """The function for positioning the menu (may be None)."""
        
    size = property(lambda self : self.get_attribute('size'), 
                    lambda self, size : self.set_attribute('size', size))
    """The size of the icons.""" 
    
    vertical = property(lambda self : self.edge in (LEFT, RIGHT))
    """
    C{True} if the icons are on a vertical panel, that is: the edge is either
    LEFT or RIGHT.
    """

    hidden = property(lambda self : self.get_attribute('hidden'), 
                    lambda self, hidden : self.set_attribute('hidden', hidden))
    """C{True} if all icons except the main icon should be hidden."""
