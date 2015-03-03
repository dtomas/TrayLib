from traylib.config import Config


class ItemState(Config):
    __states = {}
    
    @classmethod
    def get(cls, item_id = None):
        if item_id:
            return ItemState.__states.get(cls.__name__, {}).get(item_id)
        else:
            return ItemState.__states.get(cls.__name__, {}).iteritems()

    def __new__(cls, item):
        state = ItemState.__states.get(cls.__name__, {}).get(item.id)
        #print state
        if state:
            return state
        return Config.__new__(cls)

    def __init__(self, item):
        item_id = item.id
        cls = self.__class__
        if cls.__states.get(cls.__name__, {}).get(item_id) == self:
            return
        Config.__init__(self)
        self.__item = item
        cls.__states.setdefault(cls.__name__, {})[item_id] = self
        
    def destroy(self):
        del ItemState.__states.get(self.__class__.__name__, {})[self.item.id]

    item = property(lambda self : self.__item)
