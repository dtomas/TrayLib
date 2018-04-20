from gi.repository import GObject

from traylib.item import Item
from traylib.item_box import ItemBox


class Tray(GObject.Object):

    def __init__(self):
        """
        Initialize a Tray.
        """
        GObject.Object.__init__(self)
        self.__boxes = []
        self.__box_handlers = {}

    def add_box(self, box):
        self.__boxes.append(box)
        self.__box_handlers[box] = [
            box.connect("item-added", self.__box_item_added),
            box.connect("item-removed", self.__box_item_removed),
            box.connect("destroyed", self.remove_box),
        ]
        self.emit("box-added", box)

    def __box_item_added(self, box, item):
        self.emit("item-added", box, item)

    def __box_item_removed(self, box, item):
        self.emit("item-removed", box, item)

    def remove_box(self, box):
        self.__boxes.remove(box)
        for handler in self.__box_handlers.pop(box):
            box.disconnect(handler)
        self.emit("box-removed", box)

    def reorder_box(self, box, position):
        self.__boxes.remove(box)
        self.__boxes.insert(position, box)
        self.emit("box-reordered", box, position)

    def get_box(self, box_id):
        for box in self.__boxes:
            if box.id == box_id:
                return box
        return None

    def destroy(self):
        for box in self.__boxes:
            box.destroy()
        self.emit("destroyed")


    # Properties:

    boxes = property(lambda self: self.__boxes)
    """The tray's L{ItemBox}es."""


GObject.type_register(Tray)
GObject.signal_new(
    "box-added", Tray, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
    (ItemBox,)
)
GObject.signal_new(
    "box-removed", Tray, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
    (ItemBox,)
)
GObject.signal_new(
    "box-reordered", Tray, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
    (ItemBox, GObject.TYPE_INT)
)
GObject.signal_new(
    "item-added", Tray, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
    (ItemBox, Item)
)
GObject.signal_new(
    "item-removed", Tray, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
    (ItemBox, Item)
)
GObject.signal_new(
    "destroyed", Tray, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()
)
