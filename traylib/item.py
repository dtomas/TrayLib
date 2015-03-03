
class Item(object):
    
    def __init__(self, id):
        object.__init__(self)
        self.__id = id
        
    id = property(lambda self : self.__id)
