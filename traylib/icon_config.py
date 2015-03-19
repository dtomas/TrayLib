import gtk

from traylib import LEFT, RIGHT, TOP, BOTTOM, pixmaps
from traylib.config import Config, Attribute


class IconConfig(Config):
    """
    Icon configuration object.
    """

    arrow = property(lambda self : self.__arrow)
    """The arrow pixmap."""

    size = Attribute(default=32)
    """The size of the icons.""" 

    edge = Attribute(default=0)
    """
    The edge of the screen where the icons are put. One of C{0}, C{TOP},
    C{BOTTOM}, C{LEFT}, C{RIGHT}.
    """

    effects = Attribute(default=True)
    """C{True} if effects such as smooth zooming should be shown."""

    hidden = Attribute(default=False)
    """C{True} if all icons except the main icon should be hidden."""

    pos_func = Attribute(default=None)
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
        self.add_configurable(self)
        self.update_option_edge()

    def update_option_edge(self):
        edge = self.edge
        if edge == LEFT:
            pixmap = pixmaps.right
        elif edge == RIGHT:
            pixmap = pixmaps.left
        elif edge == TOP:
            pixmap = pixmaps.down
        else:
            pixmap = pixmaps.up
        self.__arrow = gtk.gdk.pixbuf_new_from_xpm_data(pixmap)
