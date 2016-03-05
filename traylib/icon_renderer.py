import gtk
import gobject

from traylib.icon import Icon


def render_icon(item, icon_config):
    """
    Render the given item as an icon.

    @param item: The L{Item} to be rendered.
    @param icon_config: The L{IconConfig} configuring the icon.

    @return: A managed L{Icon}.
    """

    def update_edge(icon_config):
        icon.edge = icon_config.edge

    def update_effects(icon_config):
        icon.effects = icon_config.effects

    def update_size(icon_config):
        update_icon(item)
        icon.size = icon_config.size

    icon_config_handlers = [
        icon_config.connect("edge-changed", update_edge),
        icon_config.connect("effects-changed", update_effects),
        icon_config.connect("size-changed", update_size),
    ]

    class state:
        menu = None
        menu_visible = False
        arrow_blink_event = 0
        button_pressed = False

    def update_name(item):
        icon.tooltip = item.get_name()

    def update_icon(item):
        pixbuf = item.get_icon(int(icon_config.size * 1.5))
        if pixbuf is not None:
            icon.pixbuf = pixbuf
            icon.alpha = 128 if item.is_greyed_out() else 255

    def update_emblem(item):
        icon.emblem = item.get_emblem()

    def update_zoom(item):
        icon.zoom_factor = 1.5 if state.menu_visible else item.get_zoom()

    def update_has_arrow(item):
        icon.has_arrow = item.has_arrow()

    def update_visibility(item):
        if item.is_visible():
            icon.show()
        else:
            icon.hide()

    def update_blinking(item):
        icon.set_blinking(item.is_blinking())

    def update_drag_source(item):
        icon.drag_source_set(
            gtk.gdk.BUTTON1_MASK,
            item.get_drag_source_targets(),
            item.get_drag_source_actions()
        )

    def update_drop_target(item):
        icon.is_drop_target = item.is_drop_target()

    def blink_arrow():
        running = (state.arrow_blink_event != 0)
        icon.has_arrow = not icon.has_arrow
        if not running:
            update_has_arrow(item)
        return running

    def update_arrow_blinking(item):
        if item.is_arrow_blinking():
            if state.arrow_blink_event == 0:
                state.arrow_blink_event = gobject.timeout_add(500, blink_arrow)
        else:
            state.arrow_blink_event = 0

    def changed(item, props):
        if "icon" in props or "is-greyed-out" in props:
            update_icon(item)
        if "zoom" in props:
            update_zoom(item)
        if "has-arrow" in props:
            update_has_arrow(item)
        if "is-visible" in props:
            update_visibility(item)
        if "is-blinking" in props:
            update_blinking(item)
        if "emblem" in props:
            update_emblem(item)
        if "drag-source" in props:
            update_drag_source(item)
        if "drop-target" in props:
            update_drop_target(item)
        if "is-arrow-blinking" in props:
            update_arrow_blinking(item)

    def destroyed(item):
        icon.destroy()

    item_handlers = [
        item.connect("changed", changed),
        item.connect("destroyed", destroyed),
    ]

    icon = Icon()
    
    def on_button_press(icon, button, time):
        state.button_pressed = True

    def on_button_release(icon, button, time):
        if not state.button_pressed:
            # When deactivating the menu, on_button_press() is not called.
            # In that case we do not want to show the menu again.
            return
        state.button_pressed = False
        menu = None
        if button == 1:
            menu = item.get_menu_left()
        elif button == 3:
            menu = item.get_menu_right()
        if menu is not None:
            def menu_deactivate(menu):
                state.menu_visible = False
                update_zoom(item)
            state.menu = menu
            state.menu_visible = True
            update_zoom(item)
            menu.connect("deactivate", menu_deactivate)
            menu.show_all()
            menu.popup(None, None, icon_config.pos_func, button, time)
        elif button == 1:
            item.click(time)

    def on_scroll_event(icon, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            item.mouse_wheel_up(event.time)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            item.mouse_wheel_down(event.time)

    def on_uris_dropped(icon, uri_list, action):
        item.uris_dropped(uri_list, action)

    def on_spring_open(icon, time):
        item.spring_open(time)

    def on_drag_data_get(icon, context, data, info, time):
        item.drag_data_get(context, data, info, time)

    def on_destroy(icon):
        for handler in icon_config_handlers:
            icon_config.disconnect(handler)
        for handler in item_handlers:
            item.disconnect(handler)

    icon.connect("button-press", on_button_press)
    icon.connect("button-release", on_button_release)
    icon.connect("scroll-event", on_scroll_event)
    icon.connect("uris-dropped", on_uris_dropped)
    icon.connect("spring-open", on_spring_open)
    icon.connect("drag-data-get", on_drag_data_get)
    icon.connect("destroy", on_destroy)

    update_edge(icon_config)
    update_effects(icon_config)
    update_size(icon_config)
    update_name(item)
    update_icon(item)
    update_zoom(item)
    update_has_arrow(item)
    update_visibility(item)
    update_blinking(item)
    update_drag_source(item)
    update_drop_target(item)
    update_arrow_blinking(item)

    return icon
