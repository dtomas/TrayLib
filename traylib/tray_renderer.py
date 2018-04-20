from gi.repository import Gtk

from traylib import LEFT, RIGHT


def render_tray(tray, icon_config, tray_config, render_item_box, render_item):
    """
    Render a L{Tray} to a C{Gtk.Box}.

    @param tray: The L{Tray} to render.
    @param icon_config: The L{IconConfig} configuring the icons.
    @param tray_config: The L{TrayConfig} configuring the tray.
    @param render_item_box: Callable rendering an L{ItemBox}.
    @param render_item: Callable rendering an L{Item}.

    @return: A managed C{Gtk.Box}.
    """

    if icon_config.vertical:
        main_box = Gtk.VBox()
        box_left = Gtk.VBox()
        box = Gtk.VBox()
        box_right = Gtk.VBox()
        separator_left = Gtk.HSeparator()
        separator_right = Gtk.HSeparator()
    else:
        main_box = Gtk.HBox()
        box_left = Gtk.HBox()
        box = Gtk.HBox()
        box_right = Gtk.HBox()
        separator_left = Gtk.VSeparator()
        separator_right = Gtk.VSeparator()

    main_box.pack_start(box_left, True, True, 0)
    main_box.pack_start(box, True, True, 0)
    main_box.pack_start(box_right, True, True, 0)

    main_box.show()
    box_left.show()
    box.show()
    box_right.show()

    def separators_changed(tray_config):
        separators = tray_config.separators
        if separators & LEFT:
            if separator_left not in box_left.get_children():
                box_left.pack_start(separator_left, True, True, 0)
                separator_left.show()
        else:
            if separator_left in box_left.get_children():
                box_left.remove(separator_left)

        if separators & RIGHT:
            if separator_right not in box_right.get_children():
                box_right.pack_end(separator_right, True, True, 0)
                separator_right.show()
        else:
            if separator_right in box_right.get_children():
                box_right.remove(separator_right)

    tray_config_handlers = [
        tray_config.connect(
            "separators-changed", separators_changed
        ),
    ]

    box_widgets = {}

    def box_added(tray, item_box):
        widget = box_widgets[item_box] = render_item_box(item_box)
        box.pack_start(widget, True, True, 0)

    def box_removed(tray, item_box):
        widget = box_widgets.pop(item_box)
        widget.destroy()

    def box_reordered(tray, item_box, position):
        widget = box_widgets[item_box]
        box.reorder_child(widget, position)

    def destroyed(tray):
        main_box.destroy()

    tray_handlers = [
        tray.connect("box-added", box_added),
        tray.connect("box-removed", box_removed),
        tray.connect("box-reordered", box_reordered),
        tray.connect("destroyed", destroyed),
    ]

    def main_box_destroyed(main_box):
        for handler in tray_config_handlers:
            tray_config.disconnect(handler)
        for handler in tray_handlers:
            tray.disconnect(handler)

    main_box.connect("destroy", main_box_destroyed)

    separators_changed(tray_config)
    # menus_changed(tray_config)

    for item_box in tray.boxes:
        box_added(tray, item_box)

    return main_box
