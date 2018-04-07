from gi.repository import GObject

from traylib.item import Item


class ItemBox(GObject.Object):
    """Logical representation of a box containing items."""

    def __init__(self, box_id):
        GObject.Object.__init__(self)
        self.__box_id = box_id
        self.__items = []

    def add_item(self, item):
        """
        Add an item to the box.
        Emits "item-added".

        @param item: The L{Item} to add.
        """
        self.__items.append(item)
        item.connect("destroyed", self.remove_item)
        self.emit("item-added", item)

    def remove_item(self, item):
        """
        Remove an item from the box.
        Emits "item-removed".

        @param item: The L{Item} to remove.
        """
        self.__items.remove(item)
        self.emit("item-removed", item)

    def reorder_item(self, item, position):
        """
        Reorder an item.
        Emits "item-reordered".

        @param item: The L{Item} to reorder.
        @param position: The new item position.
        """
        self.__items.remove(item)
        self.__items.insert(position, item)
        self.emit("item-reordered", item, position)

    def destroy(self):
        """
        Destroy the item box.
        Also destroys its items. Emits "destroyed".
        """
        for item in self.items:
            item.destroy()
        self.emit("destroyed")

    id = property(lambda self: self.__box_id)
    """The box's ID within a L{Tray}."""

    items = property(lambda self: self.__items)
    """The L{Item}s in the box."""


GObject.type_register(ItemBox)
GObject.signal_new(
    "item-added", ItemBox, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
    (Item,)
)
GObject.signal_new(
    "item-removed", ItemBox, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
    (Item,)
)
GObject.signal_new(
    "item-reordered", ItemBox, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
    (Item, GObject.TYPE_INT)
)
GObject.signal_new(
    "destroyed", ItemBox, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()
)
