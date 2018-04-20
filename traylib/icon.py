from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib

from traylib import (
    LEFT, RIGHT, TOP, BOTTOM, ICON_THEME, TARGET_URI_LIST, TARGET_MOZ_URL,
    pixmaps
)
from traylib.icon_config import IconConfig
from traylib.pixbuf_helper import scale_pixbuf_to_size


_targets = [("text/uri-list", 0, TARGET_URI_LIST),
            ("text/x-moz-url", 0, TARGET_MOZ_URL)]


MAX_SIZE = 128
"""
A pixbuf larger than this size (either in height or width) will be scaled 
down in order to speed up later scaling.
"""


# Action constants that are used to determine if an icon is in the process of 
# being shown, hidden or destroyed.
ZOOM_ACTION_NONE = 0
ZOOM_ACTION_SHOW = 1
ZOOM_ACTION_HIDE = 2
ZOOM_ACTION_DESTROY = 3


class Icon(Gtk.EventBox, object):

    def __init__(self):
        """Initialize an Icon."""

        Gtk.EventBox.__init__(self)
        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

        # image
        self.__image = Gtk.Image()
        self.__image.show()
        self.add(self.__image)
        self.__canvas = None
        self.__pixbuf = None
        self.__pixbuf_current = None
        self.__current_alpha = 0xff
        self.__target_alpha = 0xff

        # blink
        self.__blink_event = 0
        self.__blink_state = Gtk.StateType.NORMAL
        
        # mouse
        self.__mouse_over = False

        # size
        self.__size = 32

        # zoom
        self.__target_size = self.__size
        self.__current_size = 1
        self.__zoom_factor = 1.0
        self.__zoom_factor_orig = 1.0
        self.__zoom_factor_base = 1.0
        self.__zoom_action = ZOOM_ACTION_NONE
        self.__zoom_event = 0
        
        # edge
        self.__edge = 0

        # effects
        self.__effects = False

        # arrow
        self.__has_arrow = False
        self.__arrow = None
        self.__arrow_target_alpha = 0
        self.__arrow_current_alpha = 0

        # emblem
        self.__emblem_orig = None
        self.__emblem_scaled = None
        self.__emblem_target_alpha = 0
        self.__emblem_current_alpha = 0

        self.__update_max_size()
        self.__update_size_request()

        # tooltip
        self.__tooltip = ''

        self.connect("enter-notify-event", self.__enter_notify_event)
        self.connect("motion-notify-event", self.__motion)
        self.connect("leave-notify-event", self.__leave_notify_event)
        self.connect("button-press-event", self.__button_press_event)
        self.connect("button-release-event", self.__button_release_event)
        
        # dnd
        # to
        self.connect("drag-motion", self.__drag_motion)
        self.connect("drag-leave", self.__drag_leave)

        # from
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], 0)
        self.connect("drag-begin", self.__drag_begin)
        self.connect("drag-end", self.__drag_end)
        self.__is_dragged = False

        #self.connect("expose-event", self.__expose)

    def set_blinking(self, blinking, time=500):
        """
        Make the C{Icon} blink or stop it from blinking.
        
        @param blinking: If True, makes the C{Icon} blink, if False stops it
            from blinking.
        @param time: The time between two blink states (in ms).
        """
        self.__zoom_factor_orig = self.__zoom_factor_base
        def blink():
            running = (self.__blink_event != 0)
            #if not running or self.__blink_state == gtk.STATE_SELECTED:
            #    self.__blink_state = gtk.STATE_NORMAL
            #else:
            #    self.__blink_state = gtk.STATE_SELECTED
            #self.set_state(self.__blink_state)
            if not running:
                self.__zoom_factor_base = self.__zoom_factor_orig
            else:
                if self.__zoom_factor_base == self.__zoom_factor_orig * 0.5:
                    self.__zoom_factor_base = self.__zoom_factor_orig * 1.5
                else:
                    self.__zoom_factor_base = self.__zoom_factor_orig * 0.5
            self.__update_zoom_factor()
            self._refresh(True)
            return running
        if blinking:
            if self.__blink_event == 0:
                self.__blink_event = GLib.timeout_add(time, blink)
        else:
            self.__blink_event = 0

    @property
    def emblem(self):
        return self.__emblem_orig

    @emblem.setter
    def emblem(self, emblem):
        old_emblem = self.__emblem_orig
        self.__emblem_orig = emblem
        if self.__emblem_orig is not None:
            self.__emblem_scaled = scale_pixbuf_to_size(
                self.__emblem_orig, self.__max_size/3, scale_up=False
            )

        self.__update_emblem_target_alpha()
        self._refresh(self.__emblem_orig != old_emblem)

        assert (
            self.__emblem_orig is self.__emblem_scaled is None or
            self.__emblem_orig is not None and self.__emblem_scaled is not None
        )

    @property
    def pixbuf(self):
        return self.__pixbuf

    @pixbuf.setter
    def pixbuf(self, pixbuf):
        old_pixbuf = self.__pixbuf
        self.__pixbuf = pixbuf
        if (self.__pixbuf is not None and (
                self.__pixbuf.get_width() >= MAX_SIZE or
                self.__pixbuf.get_height() >= MAX_SIZE)):
            self.__pixbuf = scale_pixbuf_to_size(
                self.__pixbuf, MAX_SIZE, False
            )
        if old_pixbuf is not self.__pixbuf:
            self.__pixbuf_current = None
        self._refresh(self.__pixbuf is not old_pixbuf)

    @property
    def has_arrow(self):
        return self.__has_arrow

    @has_arrow.setter
    def has_arrow(self, has_arrow):
        old_has_arrow = self.__has_arrow
        self.__has_arrow = has_arrow
        self.__update_arrow_target_alpha()
        self._refresh()

    @property
    def tooltip(self):
        return self.__tooltip

    @tooltip.setter
    def tooltip(self, tooltip):
        self.__tooltip = tooltip
        self.set_tooltip_text(tooltip)

    @property
    def zoom_factor(self):
        return self.__zoom_factor

    @zoom_factor.setter
    def zoom_factor(self, zoom_factor):
        old_zoom_factor = self.__zoom_factor_base
        self.__zoom_factor_base = self.__zoom_factor_orig = (
            max(0.0, min(zoom_factor, 1.5))
        )
        if old_zoom_factor != self.__zoom_factor_base:
            self.__update_zoom_factor()

    def get_pointer(self):
        client_pointer = Gdk.Display.get_default().get_default_seat().get_pointer()
        __, px, py, __ = self.get_window().get_device_position(client_pointer)
        return px, py

    def __update_zoom_factor(self):
        if self.__effects and self.__mouse_over:
            px, py = self.get_pointer()
            hsize = float(self.__max_size) / 2.0
            fract_x = (hsize - (1.0 / hsize) * (px - hsize) ** 2) / hsize
            fract_y = (hsize - (1.0 / hsize) * (py - hsize) ** 2) / hsize
            edge = self.__edge
            if edge == TOP and py < hsize or edge == BOTTOM and py > hsize:
                fract = fract_x
            elif edge == LEFT and px < hsize or edge == RIGHT and px > hsize:
                fract = fract_y
            else:
                fract = fract_x * fract_y
            fract = max(0.0, fract)
            self.__zoom_factor = self.__zoom_factor_base * (1.0 + fract/2.0)
        else:
            self.__zoom_factor = self.__zoom_factor_base
        self._refresh()

    @property
    def edge(self):
        return self.__edge

    @edge.setter
    def edge(self, edge):
        self.__edge = edge
        if edge == LEFT:
            pixmap = pixmaps.right
        elif edge == RIGHT:
            pixmap = pixmaps.left
        elif edge == TOP:
            pixmap = pixmaps.down
        else:
            pixmap = pixmaps.up
        self.__arrow = GdkPixbuf.Pixbuf.new_from_xpm_data(pixmap)
        self._refresh(True)

    @property
    def effects(self):
        return self.__effects

    @effects.setter
    def effects(self, effects):
        self.__effects = effects
        self._refresh(True)

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        self.__size = size
        self.__update_max_size()
        self.__update_size_request()
        self.pixbuf = self.__pixbuf
        self.emblem = self.__emblem_orig

    @property
    def vertical(self):
        return self.edge in {LEFT, RIGHT}

    @property
    def alpha(self):
        return self.__target_alpha

    @alpha.setter
    def alpha(self, alpha):
        if self.__target_alpha == alpha:
            return
        self.__target_alpha = alpha
        self._refresh()

    def __update_arrow_target_alpha(self):
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY): 
            return
        if self.__has_arrow:
            self.__arrow_target_alpha = 255
        else:
            self.__arrow_target_alpha = 0

    def __update_canvas(self):
        if (self.__zoom_action == ZOOM_ACTION_NONE or
                self.__emblem_scaled and self.__emblem_current_alpha > 0):
            width = self.__max_size
            height = self.__max_size
        else:
            if self.__edge in (0, TOP, BOTTOM):
                width = min(int(self.__current_size * 1.5), self.__max_size)
                height = self.__max_size
            else:
                width = self.__max_size
                height = min(int(self.__current_size * 1.5), self.__max_size)
        if (self.__canvas and
                self.__canvas.get_width() == width and
                self.__canvas.get_height() == height):
            return
        self.__canvas = GdkPixbuf.Pixbuf.new(
            GdkPixbuf.Colorspace.RGB, True, 8, width, height
        )

    def __update_emblem_target_alpha(self):
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY): 
            return
        if self.__emblem_orig:
            self.__emblem_target_alpha = 196
        else:
            self.__emblem_target_alpha = 0
            
    def __update_max_size(self):
        self.__max_size = int(self.__size*1.5)

    def __update_mouse_over(self, event = None):
        if event:
            px = event.x
            py = event.y
        else:
            px, py = self.get_pointer()
        i, i, w, h = self.get_window().get_geometry()
        self.__mouse_over = (py >= 0 and py < h and px >= 0 and px < w)
        self.__update_zoom_factor()

    def __update_size_request(self):
        if self.__zoom_action != ZOOM_ACTION_NONE:
            return
        if self.vertical:
            self.set_size_request(-1, self.__max_size)
        else:
            self.set_size_request(self.__max_size, -1)

    def _refresh(self, force=False):
        """
        Refresh the C{Icon}.

        @param force: If True, forces refresh even if the icon has the right 
            size.
        """
        if not self.__pixbuf:
            return
        if not int(self.get_property('visible')):
            return

        effects = self.__effects

        if self.__zoom_action not in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY):
            self.__target_size = max(
                1, min(
                    int(self.__size * self.__zoom_factor), 
                    self.__max_size - 2
                )
            )
            if (not force and
                    self.__current_size == self.__target_size and
                    self.__arrow_current_alpha == self.__arrow_target_alpha and
                    self.__emblem_current_alpha == self.__emblem_target_alpha and
                    self.__current_alpha == self.__target_alpha):
                return

        if self.__zoom_event != 0:
            return

        if effects:            
            if self.__refresh():
                self.__zoom_event = GLib.timeout_add(6, self.__refresh)
        else:
            self.__arrow_current_alpha = self.__arrow_target_alpha
            self.__emblem_current_alpha = self.__emblem_target_alpha
            self.__current_alpha = self.__target_alpha
            self.__current_size = self.__target_size
            self.__pixbuf_current = None
            while self.__refresh():
                pass

    def __refresh(self):
        if not self.__pixbuf:
            return False

        edge = self.__edge

        if (not self.__pixbuf_current or
                self.__current_size != self.__target_size):
            self.__pixbuf_current = scale_pixbuf_to_size(
                self.__pixbuf, self.__current_size
            )
        self.__update_canvas()
        self.__canvas.fill(0x000000)
        canvas_width = self.__canvas.get_width()
        canvas_height = self.__canvas.get_height()
        width = self.__pixbuf_current.get_width()
        height = self.__pixbuf_current.get_height()
        x = int(round(float(canvas_width)/2.0) 
                - round(float(width)/2.0))
        y = int(round(float(canvas_height)/2.0) 
                - round(float(height)/2.0))
        self.__pixbuf_current.composite(
            self.__canvas, x, y, width, height, x, y, 1.0, 1.0,
            GdkPixbuf.InterpType.TILES, self.__current_alpha
        )
        if self.__emblem_current_alpha > 0:
            width = self.__max_size/3
            height = width
            self.__emblem_scaled.composite(
                self.__canvas, 0, 0, width, height, 0, 0, 1.0, 1.0,
                GdkPixbuf.InterpType.TILES, self.__emblem_current_alpha
            )
        if self.__arrow_current_alpha > 0:
            arrow = self.__arrow
            width = arrow.get_width()
            height = arrow.get_height()
            x = 0
            y = 0
            if edge in (0, TOP, BOTTOM):
                x = canvas_width/2 - width/2
                if edge == TOP:
                    y = canvas_height - height 
            if edge in (LEFT, RIGHT):
                y = canvas_height/2 - height/2
                if edge == LEFT:
                    x = canvas_width - width

            arrow.composite(
                self.__canvas, x, y, width, height, x, y, 1.0, 1.0,
                GdkPixbuf.InterpType.TILES, self.__arrow_current_alpha
            )
        self.__image.set_from_pixbuf(self.__canvas)

        if (self.__current_size == self.__target_size and
                self.__arrow_current_alpha == self.__arrow_target_alpha and
                self.__emblem_current_alpha == self.__emblem_target_alpha and
                self.__current_alpha == self.__target_alpha):
            if self.__zoom_action == ZOOM_ACTION_HIDE:
                if (self.__arrow_current_alpha > 0 or
                        self.__emblem_current_alpha > 0):
                    self.__arrow_target_alpha = 0
                    self.__emblem_target_alpha = 0
                    return True
                else:
                    if self.__current_size > 1:
                        self.__target_size = 1
                        return True
                    else:
                        Gtk.EventBox.hide(self)
            if self.__zoom_action == ZOOM_ACTION_DESTROY:
                if (self.__arrow_current_alpha > 0 or
                        self.__emblem_current_alpha > 0):
                    self.__arrow_target_alpha = 0
                    self.__emblem_target_alpha = 0
                    return True
                else:
                    if self.__current_size > 1:
                        self.__target_size = 1
                        return True
                    else:
                        Gtk.EventBox.destroy(self)
            zoom_action = self.__zoom_action
            self.__zoom_action = ZOOM_ACTION_NONE
            if zoom_action == ZOOM_ACTION_SHOW:
                self.__update_size_request()
            self.__zoom_event = 0
            return False

        if self.__current_size > self.__target_size:
            self.__current_size -= 1
        elif self.__current_size < self.__target_size:
            self.__current_size += 1
        if self.__current_alpha > self.__target_alpha:
            self.__current_alpha = max(
                self.__target_alpha, self.__current_alpha - 5
            )
        elif self.__current_alpha < self.__target_alpha:
            self.__current_alpha = min(
                self.__target_alpha, self.__current_alpha + 5
            )
        if self.__arrow_current_alpha > self.__arrow_target_alpha:
            self.__arrow_current_alpha = max(
                self.__arrow_target_alpha, self.__arrow_current_alpha - 5
            )
        elif self.__arrow_current_alpha < self.__arrow_target_alpha:
            self.__arrow_current_alpha = min(
                self.__arrow_target_alpha, self.__arrow_current_alpha + 5
            )
        if self.__emblem_current_alpha > self.__emblem_target_alpha:
            self.__emblem_current_alpha = max(
                self.__emblem_target_alpha, self.__emblem_current_alpha - 5
            )
        elif self.__emblem_current_alpha < self.__emblem_target_alpha:
            self.__emblem_current_alpha = min(
                self.__emblem_target_alpha, self.__emblem_current_alpha + 5
            )
        return True


    # Methods inherited from Gtk.EventBox
    
    def destroy(self):
        """Zoom out the C{Icon} before destroying it."""
        if not int(self.get_property('visible')):
            Gtk.EventBox.destroy(self)
            return
        self.set_size_request(-1, -1)
        self.__zoom_action = ZOOM_ACTION_DESTROY
        self._refresh()

    def hide(self):
        """Zoom out the C{Icon} before hiding it."""
        if not int(self.get_property('visible')):
            return
        self.set_size_request(-1, -1)
        self.__zoom_action = ZOOM_ACTION_HIDE
        self._refresh()

    def show(self):
        """Zoom in the C{Icon} after showing it."""
        self.__zoom_action = ZOOM_ACTION_SHOW
        self.__update_arrow_target_alpha()
        self.__update_emblem_target_alpha()
        if not int(self.get_property('visible')):
            self.set_size_request(-1, -1)
            self.__current_size = 1
            self.__arrow_current_alpha = 0
            self.__emblem_current_alpha = 0
            Gtk.EventBox.show(self)
        self._refresh()


    # Signal callbacks

    def __drag_leave(self, widget, context, time):
        self.__update_mouse_over()

    def __drag_motion(self, widget, context, x, y, time):
        self.__update_mouse_over()
        return False

    def __drag_begin(self, widget, context):
        assert widget is self
        self.__is_dragged = True

    def __drag_end(self, widget, context):
        assert widget is self
        self.__is_dragged = False
        self.__update_zoom_factor()

    def __button_press_event(self, widget, event):
        if self.__is_dragged:
            return False
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY): 
            return False
        self.emit("button-press", event.button, event.time)
        return False

    def __button_release_event(self, widget, event):
        if self.__is_dragged:
            return False
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY):
            return False
        if not self.__mouse_over:
            return False
        self.emit("button-release", event.button, event.time)
        self.__update_mouse_over()
        return False

    def __leave_notify_event(self, widget, event):
        if event.mode != Gdk.CrossingMode.NORMAL:
            return False
        self.__update_mouse_over(event)
        return False

    def __enter_notify_event(self, widget, event):
        self.__update_mouse_over(event)
        return False

    def __motion(self, widget, event):
        self.__update_mouse_over(event)
        return False

    def __expose(self, widget, event):
        self.__update_mouse_over()
        return False

GObject.type_register(Icon)
GObject.signal_new(
    "button-press", Icon, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
    (GObject.TYPE_INT, GObject.TYPE_LONG)
)
GObject.signal_new(
    "button-release", Icon, GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE,
    (GObject.TYPE_INT, GObject.TYPE_LONG)
)
