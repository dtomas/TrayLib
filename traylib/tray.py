import os

import gobject
import gtk
import rox

import traylib
from traylib import LEFT, RIGHT
import traylib.pixmaps as pixmaps
from traylib.config import Config
from traylib.item import Item
from traylib.tray_config import TrayConfig
from traylib.item_box import ItemBox


class Tray(gobject.GObject):

    def __init__(self):
        """
        Initialize a Tray.
        """
        gobject.GObject.__init__(self)
        self.__boxes = []

    def add_box(self, box):
        self.__boxes.append(box)
        box.connect("destroyed", self.remove_box)
        self.emit("box-added", box)

    def remove_box(self, box):
        self.__boxes.remove(box)
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


gobject.type_register(Tray)
gobject.signal_new(
    "box-added", Tray, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (ItemBox,)
)
gobject.signal_new(
    "box-removed", Tray, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (ItemBox,)
)
gobject.signal_new(
    "box-reordered", Tray, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    (ItemBox, gobject.TYPE_INT)
)
gobject.signal_new(
    "destroyed", Tray, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
