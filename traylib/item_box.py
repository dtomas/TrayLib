import gobject

from traylib.item import Item


class ItemBox(gobject.GObject):

    def __init__(self, box_id):
        gobject.GObject.__init__(self)
        self.__box_id = box_id
        self.__items = []

    def add_item(self, item):
        self.__items.append(item)
        item.connect("destroyed", self.remove_item)
        self.emit("item-added", item)

    def remove_item(self, item):
        self.__items.remove(item)
        self.emit("item-removed", item)

    def reorder_item(self, item, position):
        self.__items.remove(item)
        self.__items.insert(position, item)
        self.emit("item-reordered", item, position)

    def destroy(self):
        for item in self.items:
            item.destroy()
        self.emit("destroyed")

    id = property(lambda self: self.__box_id)

    items = property(lambda self: self.__items)


gobject.type_register(ItemBox)
gobject.signal_new(
    "item-added", ItemBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (Item,)
)
gobject.signal_new(
    "item-removed", ItemBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (Item,)
)
gobject.signal_new(
    "item-reordered", ItemBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (Item, gobject.TYPE_INT)
)
gobject.signal_new(
    "destroyed", ItemBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
