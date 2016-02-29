import gobject

from traylib.item import Item


class ItemBox(gobject.GObject):

    def __init__(self, box_id, has_separator=False):
        gobject.GObject.__init__(self)
        self.__box_id = box_id
        self.__has_separator = has_separator
        self.__items = []

    def add_item(self, item):
        self.__items.append(item)
        item.connect("destroyed", self.remove_item)
        self.emit("item-added", item)

    def remove_item(self, item):
        self.__items.remove(item)
        self.emit("item-removed", item)

    def destroy(self):
        for item in self.items:
            item.destroy()
        self.emit("destroyed")

    id = property(lambda self: self.__box_id)

    has_separator = property(lambda self: self.__has_separator)

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
    "destroyed", ItemBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
