import gtk

from traylib.pixbuf_helper import scale_pixbuf_to_size


def render_menu_item(item, has_submenu=False, size=24):
    """
    Render the given item as an image menu item.

    @param item: The L{Item} to be rendered.
    @param has_submenu: C{True} if the menu item should have the item's
        right-click menu as submenu.
    @param size: The size of the menu item's image.

    @return: a managed gtk.ImageMenuItem.
    """

    menu_item = gtk.ImageMenuItem("")

    def update_pixbuf(item):
        image = menu_item.get_image()
        if image is not None:
            image.set_from_pixbuf(
                scale_pixbuf_to_size(
                    item.get_icon(size), int(item.get_zoom() * size)
                )
            )

    def update_label(item):
        menu_item.set_label(item.get_name())
    
    def update_submenu(item):
        if has_submenu:
            menu_item.set_submenu(item.get_menu_right())

    def update_drag_source(item):
        menu_item.drag_source_set(
            gtk.gdk.BUTTON1_MASK,
            item.get_drag_source_targets(),
            item.get_drag_source_actions()
        )

    def destroyed(item):
        menu_item.destroy()

    item_handlers = [
        item.connect("name-changed", update_label),
        item.connect("icon-changed", update_pixbuf),
        item.connect("zoom-changed", update_pixbuf),
        item.connect("menu-right-changed", update_submenu),
        item.connect("drag-source-changed", update_drag_source),
        item.connect("destroyed", destroyed),
    ]

    def on_scroll_event(menu_item, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            item.mouse_wheel_up(event.time)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            item.mouse_wheel_down(event.time)

    def on_activate(menu_item):
        item.click(gtk.get_current_event_time())

    def on_drag_begin(menu_item, context):
        context.set_icon_pixbuf(item.get_icon(size), 0,0)

    def on_drag_data_get(menu_item, context, data, info, time):
        item.drag_data_get(context, data, info, time)

    def on_destroy(menu_item):
        for handler in item_handlers:
            item.disconnect(handler)

    menu_item.connect("drag-begin", on_drag_begin)
    menu_item.connect("drag-data-get", on_drag_data_get)
    menu_item.connect("scroll-event", on_scroll_event)
    if not has_submenu:
        menu_item.connect("activate", on_activate)
    menu_item.connect("destroy", on_destroy)

    update_drag_source(item)
    update_pixbuf(item)
    update_label(item)
    update_submenu(item)
    update_drag_source(item)

    menu_item.show()

    return menu_item
