

class IconManager(object):
    
    def __init__(self, tray):
        self.__tray = tray
        
    def init(self):
        """
        Initializes the icon manager, yielding C{None} as it progresses.
        """

    def quit(self):
        """
        Destroys the icon manager, yielding C{None} as it progresses.
        """
    
    def icon_added(self, icon):
        """Called when an icon has been added to the tray."""
    
    def icon_removed(self, icon):
        """Called when an icon has been removed from the tray."""

    tray = property(lambda self : self.__tray)
