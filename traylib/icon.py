import gtk
import gobject

from traylib import (
    LEFT, RIGHT, TOP, BOTTOM, TOOLTIPS, ICON_THEME, TARGET_URI_LIST,
    TARGET_MOZ_URL
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


class Icon(gtk.EventBox, object):

    def __init__(self, config):
        """
        Creates a new C{Icon}.
        
        @param config: The L{IconConfig} controlling the configuration of this
            C{Icon}.
        """

        gtk.EventBox.__init__(self)
        self.add_events(gtk.gdk.POINTER_MOTION_MASK)
        
        self.__config = config
        config.add_configurable(self)

        # image
        self.__image = gtk.Image()
        self.__image.show()
        self.add(self.__image)
        self.__canvas = None
        self.__pixbuf = None
        self.__pixbuf_current = None
        self.__has_themed_icon = False

        # blink
        self.__blink_event = 0
        self.__blink_state = gtk.STATE_NORMAL
        
        # mouse/menu
        self.__menu = None
        self.__mouse_over = False

        # zoom
        self.__target_size = config.size
        self.__current_size = 1
        self.__zoom_factor = 1.0
        self.__zoom_action = ZOOM_ACTION_NONE
        self.__zoom_event = 0
        
        # arrow
        self.__has_arrow = False
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
        self.connect("scroll-event", self.__scroll_event)
        
        # dnd
        # to
        self.__is_drop_target = False
        self.drag_dest_set(gtk.DEST_DEFAULT_HIGHLIGHT, _targets, 
                            gtk.gdk.ACTION_DEFAULT)
        self.connect("drag-motion", self.__drag_motion)
        self.connect("drag-leave", self.__drag_leave)
        self.connect("drag-data-received", self.__drag_data_received)
        self.connect("drag-drop", self.__drag_drop)
        self.__spring_open_event = 0
        
        # from
        self.drag_source_set(gtk.gdk.BUTTON1_MASK, [], 0)
        self.connect("drag-begin", self.__drag_begin)
        self.connect("drag-end", self.__drag_end)
        self.__is_dragged = False

        # theme
        self.__icon_theme_changed_handler = ICON_THEME.connect(
            "changed", self.__theme_changed
        )
        
        self.connect("destroy", self.__destroy)

    def set_blinking(self, blinking, time = 500):
        """
        Makes the C{Icon} blink or stops it from blinking.
        
        @param blinking: If True, makes the C{Icon} blink, if False stops it
            from blinking.
        @param time: The time between two blink states (in ms).
        """
        def blink():
            running = (self.__blink_event != 0)
            if not running or self.__blink_state == gtk.STATE_SELECTED:
                self.__blink_state = gtk.STATE_NORMAL
            else:
                self.__blink_state = gtk.STATE_SELECTED
            self.set_state(self.__blink_state)
            return running
        if blinking:
            if self.__blink_event == 0:
                self.__blink_event = gobject.timeout_add(time, blink)
        else:
            self.__blink_event = 0

    def update_emblem(self):
        """Updates the emblem by calling L{make_emblem()}"""
        old_emblem = self.__emblem_orig
        self.__emblem_orig = self.make_emblem()
        assert (self.__emblem_orig == None 
                or isinstance(self.__emblem_orig, gtk.gdk.Pixbuf))
        if self.__emblem_orig:
            self.__emblem_scaled = scale_pixbuf_to_size(self.__emblem_orig,
                                                        self.__max_size/3,
                                                        scale_up = False)

        self.__update_emblem_target_alpha()
        self._refresh(self.__emblem_orig != old_emblem)

        assert (self.__emblem_orig == self.__emblem_scaled == None 
                or self.__emblem_orig and self.__emblem_scaled)

    def update_icon(self):
        """Updates the icon by calling L{make_icon()}"""
        old_pixbuf = self.__pixbuf
        self.__pixbuf = self.make_icon()
        assert (self.__pixbuf == None 
                or isinstance(self.__pixbuf, gtk.gdk.Pixbuf))
        if (self.__pixbuf and (self.__pixbuf.get_width() >= MAX_SIZE 
                        or self.__pixbuf.get_height() >= MAX_SIZE)):
            self.__pixbuf = scale_pixbuf_to_size(
                self.__pixbuf, MAX_SIZE, False
            )
        if old_pixbuf != self.__pixbuf:
            self.__pixbuf_current = None
        self._refresh(self.__pixbuf != old_pixbuf)

    def update_is_drop_target(self):
        """Updates whether URIs can be dropped on the C{Icon}."""
        self.__is_drop_target = self.make_is_drop_target() 

    def update_has_arrow(self):
        """Updates the arrow by calling L{make_has_arrow()}"""
        old_has_arrow = self.__has_arrow
        self.__has_arrow = self.make_has_arrow()
        self.__update_arrow_target_alpha()
        self._refresh()

    def update_tooltip(self):
        """Updates the tooltip by calling L{make_tooltip()}"""
        self.__tooltip = self.make_tooltip()
        assert (self.__tooltip == None or isinstance(self.__tooltip, str)
                or isinstance(self.__tooltip, unicode))
        TOOLTIPS.set_tip(self, self.__tooltip)

    def update_visibility(self):
        """Updates the visibility by calling L{make_visibility()}"""
        if not self.__config.hidden and self.make_visibility():
            self.show()
        else:
            self.hide()

    def update_zoom_factor(self):
        """Updates the zoom factor by calling L{make_zoom_factor()}."""
        old_zoom_factor = self.__zoom_factor
        self.__zoom_factor = max(0.0, min(self.make_zoom_factor(), 1.5))
        assert isinstance(self.__zoom_factor, float)
        if old_zoom_factor != self.__zoom_factor:
            self._refresh()

    def __update_arrow_target_alpha(self):
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY): 
            return
        if self.__has_arrow:
            self.__arrow_target_alpha = 255
        else:
            self.__arrow_target_alpha = 0

    def __update_canvas(self):
        if (self.__zoom_action == ZOOM_ACTION_NONE 
                or self.__emblem_scaled and self.__emblem_current_alpha > 0):
            width = self.__max_size
            height = self.__max_size
        else:
            if self.__config.edge in (0, TOP, BOTTOM):
                width = min(int(self.__current_size * 1.5), self.__max_size)
                height = self.__max_size
            else:
                width = self.__max_size
                height = min(int(self.__current_size * 1.5), self.__max_size)
        if (self.__canvas 
                and self.__canvas.get_width() == width 
                and self.__canvas.get_height() == height):
            return
        self.__canvas = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                        True,
                                        8,
                                        width,
                                        height)

    def __update_emblem_target_alpha(self):
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY): 
            return
        if self.__emblem_orig:
            self.__emblem_target_alpha = 196
        else:
            self.__emblem_target_alpha = 0
            
    def __update_max_size(self):
        self.__max_size = int(self.__config.size*1.5)

    def __update_mouse_over(self, event = None):
        if event:
            px = event.x
            py = event.y
        else:
            px, py = self.get_pointer()
        i, i, w, h, i = self.window.get_geometry()
        self.__mouse_over = (py >= 0 and py < h and px >= 0 and px < w)
        self.update_zoom_factor()

    def __update_size_request(self):
        if self.__zoom_action != ZOOM_ACTION_NONE:
            return
        if self.__config.vertical:
            self.set_size_request(-1, self.__max_size)
        else:
            self.set_size_request(self.__max_size, -1)

    def _refresh(self, force=False):
        """
        Refreshes the C{Icon}.
        
        @param force: If True, forces refresh even if the icon has the right 
            size.
        """
        if not self.__pixbuf:
            return
        if not int(self.get_property('visible')):
            return
            
        effects = self.__config.effects

        if self.__zoom_action not in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY):
            self.__target_size = max(
                1, min(
                    int(self.__config.size * self.__zoom_factor), 
                    self.__max_size - 2
                )
            )
            if (not force 
                    and self.__current_size 
                        == self.__target_size 
                    and self.__arrow_current_alpha 
                        == self.__arrow_target_alpha
                    and self.__emblem_current_alpha 
                        == self.__emblem_target_alpha):
                return

        if self.__zoom_event != 0:
            return

        if effects:            
            if self.__refresh():
                self.__zoom_event = gobject.timeout_add(6, self.__refresh)
        else:
            self.__arrow_current_alpha = self.__arrow_target_alpha
            self.__emblem_current_alpha = self.__emblem_target_alpha
            self.__current_size = self.__target_size
            self.__pixbuf_current = None
            while self.__refresh():
                pass

    def __refresh(self):
        if not self.__pixbuf:
            return False

        edge = self.__config.edge

        if (not self.__pixbuf_current 
                or self.__current_size != self.__target_size):
            self.__pixbuf_current = scale_pixbuf_to_size(self.__pixbuf, 
                                                        self.__current_size)
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
        self.__pixbuf_current.composite(self.__canvas, 
                                    x, y,
                                    width, height, 
                                    x, y,
                                    1.0, 1.0, 
                                    gtk.gdk.INTERP_TILES, 
                                    255)
        if self.__emblem_current_alpha > 0:
            width = self.__max_size/3
            height = width
            self.__emblem_scaled.composite(self.__canvas, 0, 0,
                                width, height,
                                0, 0,
                                1.0, 1.0, gtk.gdk.INTERP_TILES,
                                self.__emblem_current_alpha)
        if self.__arrow_current_alpha > 0:
            arrow = self.__config.arrow
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

            arrow.composite(self.__canvas, x, y,
                                width, height,
                                x, y,
                                1.0, 1.0, 
                                gtk.gdk.INTERP_TILES,
                                self.__arrow_current_alpha)
        self.__image.set_from_pixbuf(self.__canvas)

        if (self.__current_size == self.__target_size 
                and self.__arrow_current_alpha == self.__arrow_target_alpha
                and self.__emblem_current_alpha == self.__emblem_target_alpha):
            if self.__zoom_action == ZOOM_ACTION_HIDE:
                if (self.__arrow_current_alpha > 0 
                        or self.__emblem_current_alpha > 0):
                    self.__arrow_target_alpha = 0
                    self.__emblem_target_alpha = 0
                    return True
                else:
                    if self.__current_size > 1:
                        self.__target_size = 1
                        return True
                    else:
                        gtk.EventBox.hide(self)
            if self.__zoom_action == ZOOM_ACTION_DESTROY:
                if (self.__arrow_current_alpha > 0 
                        or self.__emblem_current_alpha > 0):
                    self.__arrow_target_alpha = 0
                    self.__emblem_target_alpha = 0
                    return True
                else:
                    if self.__current_size > 1:
                        self.__target_size = 1
                        return True
                    else:
                        gtk.EventBox.destroy(self)
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
        if self.__arrow_current_alpha > self.__arrow_target_alpha:
            self.__arrow_current_alpha = max(self.__arrow_target_alpha, 
                                            self.__arrow_current_alpha - 5)
        elif self.__arrow_current_alpha < self.__arrow_target_alpha:
            self.__arrow_current_alpha = min(self.__arrow_target_alpha, 
                                            self.__arrow_current_alpha + 5)
        if self.__emblem_current_alpha > self.__emblem_target_alpha:
            self.__emblem_current_alpha = max(self.__emblem_target_alpha, 
                                            self.__emblem_current_alpha - 5)
        elif self.__emblem_current_alpha < self.__emblem_target_alpha:
            self.__emblem_current_alpha = min(self.__emblem_target_alpha, 
                                            self.__emblem_current_alpha + 5)
        return True

    def find_icon_name(self):
        for icon_name in self.get_icon_names():
            icon_info = ICON_THEME.lookup_icon(icon_name, 48, 0)
            if icon_info is not None:
                break
        return icon_name

    # Methods inherited from gtk.EventBox
    
    def destroy(self):
        """Zooms out the C{Icon} before destroying it."""
        if not int(self.get_property('visible')):
            gtk.EventBox.destroy(self)
            return
        self.set_size_request(-1, -1)
        self.__zoom_action = ZOOM_ACTION_DESTROY
        self._refresh()

    def hide(self):
        """Zooms out the C{Icon} before hiding it."""
        if not int(self.get_property('visible')):
            return
        self.set_size_request(-1, -1)
        self.__zoom_action = ZOOM_ACTION_HIDE
        self._refresh()

    def show(self):
        """Zooms in the C{Icon} after showing it."""
        self.__zoom_action = ZOOM_ACTION_SHOW
        self.__update_arrow_target_alpha()
        self.__update_emblem_target_alpha()
        if not int(self.get_property('visible')):
            self.set_size_request(-1, -1)
            self.__current_size = 1
            self.__arrow_current_alpha = 0
            self.__emblem_current_alpha = 0
            gtk.EventBox.show(self)
        self._refresh()


    # Methods called when config options of the associated IconConfig changed

    def update_option_edge(self):
        """Updates the edge the C{Icon} is at."""
        self._refresh(True)
        
    def update_option_effects(self):
        """Updates the effects of the C{Icon}."""
        self._refresh(True)

    def update_option_size(self):
        """Updates the C{Icon}'s size."""
        self.__update_max_size()
        self.__update_size_request()
        self.update_icon()
        self.update_emblem()
        
    def update_option_hidden(self):
        self.update_visibility()


    # Signal callbacks
    
    def __theme_changed(self, icon_theme):
        self.icon_theme_changed()
        if self.has_themed_icon:
            self.update_icon()

    def __destroy(self, widget):
        assert widget == self
        self.__config.remove_configurable(self)
        ICON_THEME.disconnect(self.__icon_theme_changed_handler)

    def __drag_data_received(self, widget, context, x, y, data, info, time):
        if data.data == None:
            context.drop_finish(False, time)
            return
        if self == context.get_source_widget():
            return
        uri_list = []
        if info == TARGET_MOZ_URL:
            uri_list = [
                data.data.decode('utf-16').encode('utf-8').split('\n')[0]
            ]
        elif info == TARGET_URI_LIST:
            uri_list = data.get_uris()
        self.uris_dropped(uri_list, context.action)
        context.drop_finish(True, time)

    def __drag_drop(self, widget, context, data, info, time):
        """Callback for the 'drag-drop' signal."""
        if not self.is_drop_target:
            return False
        target = widget.drag_dest_find_target(context, _targets)
        widget.drag_get_data(context, target, time)
        return True

    def __drag_leave(self, widget, context, time):
        if self.__spring_open_event == 0:
            return 
        gobject.source_remove(self.__spring_open_event)
        self.__spring_open_event = 0

    def __drag_motion(self, widget, context, x, y, time):
        if self.__spring_open_event == 0:
            self.__spring_open_event = gobject.timeout_add(
                1000, self.spring_open, time
            )
        if self.is_drop_target:
            action = context.suggested_action
        else:
            action = 0
        context.drag_status(action, time)
        return True
        
    def __drag_begin(self, widget, context):
        assert widget == self
        self.__is_dragged = True
        context.set_icon_pixbuf(self.icon, 0,0)
        
    def __drag_end(self, widget, context):
        assert widget == self
        self.__is_dragged = False
        self.update_zoom_factor()

    def __button_press_event(self, widget, event):
        if self.__is_dragged:
            return False
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY): 
            return False
        
        button = event.button
        
        if button == 4:
            self.mouse_wheel_up()
        elif button == 5:
            self.mouse_wheel_down()
        elif button == 3 or button == 1:
            self.__show_menu(button, event.time)
        return False

    def __show_menu(self, button, time):
        assert button in (1,3)
        if button == 1:
            menu = self.get_menu_left()
        elif button == 3:
            menu = self.get_menu_right()
        if menu:
            def menu_deactivate(menu):
                self.__menu = None
                self.__update_mouse_over()
            menu.connect("deactivate", menu_deactivate)
            menu.show_all()
            menu.popup(None, None, self.__config.pos_func, 
                                    button, 
                                    time)
            self.__menu = menu
            self.update_zoom_factor()

    def __button_release_event(self, widget, event):
        if self.__is_dragged:
            return False
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY):
            return False
        if not self.__mouse_over or self.__menu:
            return False
        if event.button == 1:
            self.click(event.time)
        self.__update_mouse_over()
        return False

    def __leave_notify_event(self, widget, event):
        if event.mode != gtk.gdk.CROSSING_NORMAL:
            return False
        self.__update_mouse_over(event)
        return False

    def __enter_notify_event(self, widget, event):
        self.__update_mouse_over(event)
        return False

    def __motion(self, widget, event):
        self.__update_mouse_over(event)
        return False

    def __scroll_event(self, widget, event):
        if self.__zoom_action in (ZOOM_ACTION_HIDE, ZOOM_ACTION_DESTROY):
            return False
        if event.direction == gtk.gdk.SCROLL_UP:
            self.mouse_wheel_up(event.time)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.mouse_wheel_down(event.time)
        return False


    # Methods to be implemented or extended by subclasses
    
    def get_icon_names(self):
        """
        Override this to determine the icon's icon names. These will only be 
        used if L{get_icon_path} doesn't return a path to an icon or the icon
        could not be loaded.

        @return The icon names.
        """
        return []

    def get_icon_path(self):
        """
        Override this to determine the path to a file from which the pixbuf 
        will be loaded.
        """
        return None

    def get_icon_pixbuf(self):
        """
        Override this to determine the pixbuf to be used for the icon. This
        will only be used if no icons could be found for the icon names
        returned by L{get_icon_names()} and L{get_icon_path()} doesn't return
        a path to an icon.
        """
        return None

    def get_menu_right(self):
        """
        Override this to determine the menu that pops up when right-clicking
        the C{Icon}.

        @return: The menu that pops up when right-clicking the C{Icon}.
        """
        return None

    def get_menu_left(self):
        """
        Override this to determine the menu that pops up when left-clicking the
        C{Icon}. (In case the C{click()} method returned C{False}.)

        @return: The menu that pops up when left-clicking the C{Icon}.
        """
        return None
    
    def icon_theme_changed(self):
        """
        Override this to perform an action when the icon theme has changed.
        """
        pass

    def click(self, time = 0L):
        """
        Override this to determine the action when left-clicking the C{Icon}. 
        If an action was performed, return C{True}, else return C{False}.
        
        @param time: The time of the click event.
        """
        return False

    def mouse_wheel_up(self, time = 0L):
        """
        Override this to determine the action when the mouse wheel is scrolled 
        up.
        
        @param time: The time of the scroll event.
        """
        return False

    def mouse_wheel_down(self, time = 0L):
        """
        Override this to determine the action when the mouse wheel is scrolled 
        down.
        
        @param time: The time of the scroll event.
        """
        return False

    def uris_dropped(self, uris, action=gtk.gdk.ACTION_COPY):
        """
        Override this to react to URIs being dropped on the C{Icon}.
        
        @param uris: A list of URIs.
        @param action: One of C{gtk.gdk.ACTION_COPY}, C{gtk.gdk.ACTION_MOVE}
            or C{gtk.gdk.ACTION_LINK}.
        """
        pass

    def spring_open(self, time = 0L):
        """
        Override this to determine the action when the mouse pointer stays on
        an icon some time while dragging.
        
        @return: C{True} if C{spring_open()} should be called again in a
            second. 
        """
        return False

    def make_emblem(self):
        """
        Override this to determine the emblem to be shown in the upper left 
        corner.
        
        @return: The new emblem.
        """
        return None

    def make_has_arrow(self):
        """
        Override this to determine whether the C{Icon} has an arrow or not.
        
        @return: C{True} if the C{Icon} should have an arrow.
        """
        return False

    def make_icon(self):
        """
        This determines the C{gtk.gdk.Pixbuf} the C{Icon} should have.
        By default, this method tries to load the pixbuf from the path
        returned by L{get_icon_path()}. If this fails, it looks up the icon 
        in the current icon theme from the icon names returned by 
        L{get_icon_names()}. If this also fails, it returns the pixbuf
        returned by L{get_icon_pixbuf()}.
        
        @return: The new pixbuf.
        """
        icon_path = self.icon_path
        if icon_path:
            try:
                return gtk.gdk.pixbuf_new_from_file(icon_path)
            except:
                pass
        size = self.size
        for icon_name in self.icon_names:
            icon_info = ICON_THEME.lookup_icon(icon_name, size, 0)
            if not icon_info:
                continue
            icon_path = icon_info.get_filename()
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file(icon_path)
            except:
                continue
            self.__has_themed_icon = True
            return pixbuf
        return self.icon_pixbuf

    def make_is_drop_target(self):
        """
        Override this to determine whether URIs can be dropped on the C{Icon}
        or not.
        
        @return: C{True} if URIs may be dropped on the C{Icon}.
        """
        return False

    def make_tooltip(self):
        """
        Override this to determine the tooltip.
        
        @return: The new tooltip.
        """
        return None

    def make_visibility(self):
        """
        Override this to determine the visibility.
        
        @return: C{True} if the C{Icon} should be visible.
        """
        return True

    def make_zoom_factor(self):
        """
        Extend this to determine the zoom factor.
        
        @return: The new zoom factor.
        """
        if self.__menu:
            return 1.5
        if self.__config.effects and self.__mouse_over:
            px, py = self.get_pointer()
            hsize = float(self.__max_size)/2.0
            fract_x = (hsize - (1.0/hsize)*(px-hsize)**2) / hsize
            fract_y = (hsize - (1.0/hsize)*(py-hsize)**2) / hsize
            edge = self.__config.edge
            if edge == TOP and py < hsize or edge == BOTTOM and py > hsize:
                fract = fract_x
            elif edge == LEFT and px < hsize or edge == RIGHT and px > hsize:
                fract = fract_y
            else:
                fract = fract_x * fract_y
            fract = max(0.0, fract)
            return 1.0 + fract/2.0
        return 1.0

    icon = property(lambda self : self.__pixbuf)
    """The pixbuf of the C{Icon}."""

    icon_config = property(lambda self : self.__config)
    """The C{Icon}'s configuration."""
    
    icon_names = property(lambda self : self.get_icon_names())
    """The icon names returned by L{get_icon_names()}."""
    
    icon_path = property(lambda self : self.get_icon_path())
    """The icon path returned by L{get_icon_path()}."""
    
    icon_pixbuf = property(lambda self : self.get_icon_pixbuf())
    """The pixbuf returned by L{get_icon_pixbuf()}."""

    size = property(lambda self : self.__config.size)
    """The size of the C{Icon}."""

    tooltip = property(lambda self : self.__tooltip)
    """The tooltip of the C{Icon}."""
    
    has_arrow = property(lambda self : self.__has_arrow)
    """C{True} if the C{Icon} has an arrow."""

    has_themed_icon = property(lambda self : self.__has_themed_icon)
    """C{True} if the C{Icon}'s pixbuf comes from an icon theme."""

    is_drop_target = property(lambda self : self.__is_drop_target)
    """C{True} if uris can be dropped on the C{Icon}."""

gobject.type_register(Icon)
