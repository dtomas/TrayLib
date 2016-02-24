import gtk

from traylib.icon import Icon


def render_icon(item, icon_config):
    """
    Render the given item as an icon.

    @param item: The L{Item} to be rendered.
    @param icon_config: The L{IconConfig} configuring the icon.

    @return: a managed L{Icon}.
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

    def update_name(item):
        icon.tooltip = item.get_name()

    def update_icon(item):
        pixbuf = item.get_icon(icon_config.size)
        if pixbuf is not None:
            icon.pixbuf = pixbuf
            icon.alpha = 128 if item.is_greyed_out() else 255

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

    def destroyed(item):
        icon.destroy()

    item_handlers = [
        item.connect("name-changed", update_name),
        item.connect("icon-changed", update_icon),
        item.connect("zoom-changed", update_zoom),
        item.connect("has-arrow-changed", update_has_arrow),
        item.connect("is-visible-changed", update_visibility),
        item.connect("is-blinking-changed", update_blinking),
        item.connect("is-greyed-out-changed", update_icon),
        item.connect("destroyed", destroyed),
    ]

    icon = Icon()
    
    def on_button_press(icon, button, time):
        menu = None
        if button == 1:
            menu = item.get_menu_left()
        elif button == 3:
            menu = item.get_menu_right()
        if menu is not None:
            def menu_deactivate(menu):
                # Cannot set state.menu to None, because this will destroy
                # the menu and its items and lead to problems with menu item
                # drag and drop.
                state.menu_visible = False
                update_zoom(item)
            state.menu = menu
            state.menu_visible = True
            update_zoom(item)
            menu.connect("deactivate", menu_deactivate)
            menu.show_all()
            menu.popup(None, None, icon_config.pos_func, button, time)

    def on_button_release(icon, button, time):
        if button == 1 and not state.menu_visible:
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

    return icon
