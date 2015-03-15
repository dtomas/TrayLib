from traylib import *
from traylib.config import Config, Attribute


class IconConfig(Config):
    """
    Icon configuration object.
    """

    arrow = property(lambda self : self.__arrow)
    """The arrow pixmap."""

    size = Attribute('update_option_size')
    """The size of the icons.""" 

    edge = Attribute('update_option_edge')
    """
    The edge of the screen where the icons are put. One of C{0}, C{TOP},
    C{BOTTOM}, C{LEFT}, C{RIGHT}.
    """

    effects = Attribute('update_option_effects')
    """C{True} if effects such as smooth zooming should be shown."""

    hidden = Attribute('update_option_hidden')
    """C{True} if all icons except the main icon should be hidden."""

    pos_func = Attribute()
    """The function for positioning the menu (may be None)."""
    
    vertical = property(lambda self : self.edge in (LEFT, RIGHT))
    """
    C{True} if the icons are on a vertical panel, that is: the edge is either
    LEFT or RIGHT.
    """

    # Constructor is kept for compatibility reasons, as there might be clients
    # passing positional parameters.
    def __init__(self, size, edge, effects, pos_func, hidden):
        assert size > 0
        assert edge in (0, TOP, BOTTOM, LEFT, RIGHT)
        Config.__init__(self, size=size, edge=edge, effects=effects,
                        pos_func=pos_func, hidden=hidden)
        self.__arrow = None

    def arrow_changed(self, old_edge, edge):
        if edge == LEFT:
            pixmap = pixmaps.right
        elif edge == RIGHT:
            pixmap = pixmaps.left
        elif edge == TOP:
            pixmap = pixmaps.down
        else:
            pixmap = pixmaps.up
        self.__arrow = gtk.gdk.pixbuf_new_from_xpm_data(pixmap)
