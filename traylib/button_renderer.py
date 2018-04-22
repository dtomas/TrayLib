from gi.repository import Gtk, Gdk, GLib

from traylib.pixbuf_helper import change_alpha, scale_pixbuf_to_size
from traylib import TOP, BOTTOM, LEFT, RIGHT

_arrow_icon_names = {
    0: "pan-up-symbolic",
    BOTTOM: "pan-up-symbolic",
    TOP: "pan-down-symbolic",
    LEFT: "pan-right-symbolic",
    RIGHT: "pan-left-symbolic",
}


def render_button(
        item, icon_config, arrow_icon_size=1, arrow_padding=3,
        arrow_icon_names=_arrow_icon_names):
    """
    Render the given item as a button.

    @param item: The L{Item} to be rendered.
    @param icon_config: The L{IconConfig} configuring the icon.

    @return: A managed L{Gtk.Button}.
    """

    def update_size(icon_config):
        update_icon(item)

    def update_edge(icon_config):
        arrow.set_from_icon_name(
            _arrow_icon_names[icon_config.edge],
            arrow_icon_size,
        )
        update_size(icon_config)

    icon_config_handlers = [
        icon_config.connect("size-changed", update_size),
        icon_config.connect("edge-changed", update_edge),
    ]

    class state:
        menu = None
        menu_visible = False
        blink_event = 0
        arrow_blink_event = 0
        button_pressed = False
        base_pixbuf = None

    def update_name(item):
        button.set_tooltip_text(item.get_name())

    def update_pixbuf(item):
        if state.base_pixbuf is None:
            return
        pixbuf = state.base_pixbuf
        if item.is_minimized():
            pixbuf = scale_pixbuf_to_size(
                pixbuf, int(icon_config.size) * 0.66
            )
        if item.is_greyed_out():
            pixbuf = change_alpha(pixbuf, 128)
        state.pixbuf = pixbuf
        image.set_from_pixbuf(pixbuf)

    def update_is_active(item):
        if state.menu_visible or item.is_active():
            button.set_state_flags(Gtk.StateFlags.CHECKED, False)
        else:
            button.unset_state_flags(Gtk.StateFlags.CHECKED)

    def update_icon(item):
        state.base_pixbuf = item.get_icon(int(icon_config.size))
        update_pixbuf(item)

    #def update_emblem(item):
    #    icon.emblem = item.get_emblem()

    def update_has_arrow(item):
        if item.has_arrow():
            arrow.show()
        else:
            arrow.hide()

    def update_visibility(item):
        if item.is_visible():
            button.show()
        else:
            button.hide()

    def blink():
        blinking = item.is_blinking()
        if not blinking or button.get_state_flags() & Gtk.StateFlags.PRELIGHT:
            button.unset_state_flags(Gtk.StateFlags.PRELIGHT)
        else:
            button.set_state_flags(Gtk.StateFlags.PRELIGHT, False)
        return blinking

    def update_blinking(item):
        if state.blink_event == 0:
            state.blink_event = GLib.timeout_add(500, blink)
        else:
            state.blink_event = 0

    def update_drag_source(item):
        button.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK,
            item.get_drag_source_targets(),
            item.get_drag_source_actions()
        )

    #def blink_arrow():
    #    running = (state.arrow_blink_event != 0)
    #    icon.has_arrow = not icon.has_arrow
    #    if not running:
    #        update_has_arrow(item)
    #    return running

    #def update_arrow_blinking(item):
    #    if item.is_arrow_blinking():
    #        if state.arrow_blink_event == 0:
    #            state.arrow_blink_event = GLib.timeout_add(500, blink_arrow)
    #    else:
    #        state.arrow_blink_event = 0

    def changed(item, props):
        if "icon" in props:
            update_icon(item)
        if "is-greyed-out" in props:
            update_pixbuf(item)
        if "is-active" in props:
            update_is_active(item)
        if "is-minimized" in props:
            update_pixbuf(item)
        if "has-arrow" in props:
            update_has_arrow(item)
        if "is-visible" in props:
            update_visibility(item)
        if "is-blinking" in props:
            update_blinking(item)
        #if "emblem" in props:
        #    update_emblem(item)
        if "drag-source" in props:
            update_drag_source(item)
        #if "is-arrow-blinking" in props:
        #    update_arrow_blinking(item)

    def destroyed(item):
        button.destroy()

    item_handlers = [
        item.connect("changed", changed),
        item.connect("destroyed", destroyed),
    ]

    button = Gtk.Button.new()
    image = Gtk.Image.new()
    arrow = Gtk.Image.new()
    arrow.set_opacity(0.5)
    overlay = Gtk.Overlay.new()
    overlay.add(button)
    overlay.add_overlay(arrow)
    overlay.set_overlay_pass_through(button, False)
    overlay.set_overlay_pass_through(arrow, True)
    button.set_image(image)
    button.set_relief(Gtk.ReliefStyle.NONE)
    button.set_can_focus(False)
    button.show()
    overlay.show()

    def on_button_press(button, event):
        state.button_pressed = True

    def on_activate(button):
        item.click(0)

    def on_button_release(button, event):
        if not state.button_pressed:
            # When deactivating the menu, on_button_press() is not called.
            # In that case we do not want to show the menu again.
            return
        state.button_pressed = False
        menu = None
        if event.button == 1:
            menu = item.get_menu_left()
        elif event.button == 3:
            menu = item.get_menu_right()
        if menu is None:
            return
        def menu_deactivate(menu):
            state.menu_visible = False
            update_is_active(item)
        state.menu = menu
        state.menu_visible = True
        update_is_active(item)
        menu.connect("deactivate", menu_deactivate)
        menu.show_all()
        menu.popup(
            None, None, icon_config.pos_func,
            None, event.button, event.time
        )

    def on_scroll_event(icon, event):
        if event.direction == Gdk.ScrollDirection.UP:
            item.mouse_wheel_up(event.time)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            item.mouse_wheel_down(event.time)

    def on_drag_begin(button, context):
        Gtk.drag_set_icon_pixbuf(context, item.get_icon(48), 0, 0)

    def on_drag_data_get(button, context, data, info, time):
        item.drag_data_get(context, data, info, time)

    def on_destroy(button):
        for handler in icon_config_handlers:
            icon_config.disconnect(handler)
        for handler in item_handlers:
            item.disconnect(handler)

    def on_get_child_position(overlay, child, rect):
        allocation = button.get_allocation()
        width = allocation.width
        height = allocation.height
        _valid, arrow_width, arrow_height = Gtk.IconSize.lookup(
            arrow_icon_size
        )
        if icon_config.edge == TOP:
            rect.x = (width - arrow_width) / 2
            rect.y = height - arrow_height + arrow_padding
        elif icon_config.edge == LEFT:
            rect.x = width - arrow_width + arrow_padding
            rect.y = (height - arrow_height) / 2
        elif icon_config.edge == RIGHT:
            rect.x = arrow_padding
            rect.y = (height - arrow_height) / 2
        else:
            rect.x = (width - arrow_width) / 2
            rect.y = -arrow_padding
        rect.width = arrow_width
        rect.height = arrow_height
        return True

    button.connect("clicked", on_activate)
    button.connect("button-press-event", on_button_press)
    button.connect("button-release-event", on_button_release)
    button.connect("scroll-event", on_scroll_event)
    button.connect("drag-data-get", on_drag_data_get)
    button.connect("drag-begin", on_drag_begin)
    button.connect("destroy", on_destroy)
    overlay.connect("get-child-position", on_get_child_position)

    update_edge(icon_config)
    update_name(item)
    update_has_arrow(item)
    update_visibility(item)
    update_is_active(item)
    update_blinking(item)
    #update_emblem(item)
    update_drag_source(item)
    #update_arrow_blinking(item)

    return overlay
