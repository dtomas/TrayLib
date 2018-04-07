from gi.repository import Gtk, Gdk

from traylib.pixbuf_helper import scale_pixbuf_to_size, change_alpha


def render_menu_item(item, has_submenu=False, size=24):
    """
    Render the given item as an image menu item.

    @param item: The L{Item} to be rendered.
    @param has_submenu: C{True} if the menu item should have the item's
        right-click menu as submenu.
    @param size: The size of the menu item's image.

    @return: a managed Gtk.ImageMenuItem.
    """

    menu_item = Gtk.MenuItem()
    image = Gtk.Image()
    label = Gtk.Label()
    box = Gtk.HBox()
    box.pack_start(image, False, False, 0)
    box.pack_start(label, False, False, 0)
    menu_item.add(box)

    def update_pixbuf(item):
        pixbuf = scale_pixbuf_to_size(
            item.get_icon(size), int(item.get_zoom() * size)
        )
        if item.is_greyed_out():
            pixbuf = change_alpha(pixbuf, 128)
        image.set_from_pixbuf(pixbuf)

    def update_label(item):
        label.set_text(item.get_name())
    
    def update_submenu(item):
        if has_submenu:
            menu_item.set_submenu(item.get_menu_right())

    def update_drag_source(item):
        menu_item.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK,
            item.get_drag_source_targets(),
            item.get_drag_source_actions()
        )

    def changed(item, props):
        if "name" in props:
            update_label(item)
        if "icon" in props or "is-greyed-out" in props or "zoom" in props:
            update_pixbuf(item)
        if "menu-right" in props:
            update_submenu(item)
        if "drag-source" in props:
            update_drag_source(item)

    def destroyed(item):
        menu_item.destroy()

    item_handlers = [
        item.connect("changed", changed),
        item.connect("destroyed", destroyed),
    ]

    def on_scroll_event(menu_item, event):
        if event.direction == Gdk.ScrollDirection.UP:
            item.mouse_wheel_up(event.time)
        elif event.direction == Gdk.ScrollDirection.DOWN:
            item.mouse_wheel_down(event.time)

    def on_activate(menu_item):
        item.click(Gtk.get_current_event_time())

    def on_drag_begin(menu_item, context):
        Gtk.drag_set_icon_pixbuf(context, item.get_icon(48), 0, 0)

    def on_drag_data_get(menu_item, context, data, info, time):
        item.drag_data_get(context, data, info, time)

    def on_destroy(menu_item):
        for handler in item_handlers:
            item.disconnect(handler)

    menu_item.add_events(Gdk.EventMask.SCROLL_MASK)
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
