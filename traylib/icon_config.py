import gtk

from traylib import LEFT, RIGHT, TOP, BOTTOM
from traylib.config import Config, Attribute


class IconConfig(Config):
    """
    Icon configuration object.
    """

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
    
    vertical = property(lambda self: self.edge in (LEFT, RIGHT))
    """
    C{True} if the icons are on a vertical panel, that is: the edge is either
    LEFT or RIGHT.
    """

    def __init__(self, **kwargs):
        assert kwargs['size'] > 0
        assert kwargs['edge'] in (0, TOP, BOTTOM, LEFT, RIGHT)
        Config.__init__(self, **kwargs)
