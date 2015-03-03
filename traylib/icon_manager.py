

class IconManager(object):
    
    def __init__(self, tray):
        self.__tray = tray
        
    def init(self):
        pass
    
    def quit(self):
        pass
    
    def icon_added(self, icon):
        pass
    
    def icon_removed(self, icon):
        pass

    tray = property(lambda self : self.__tray)
