import gtk

from traylib import LEFT, RIGHT


def render_tray(tray, icon_config, tray_config, render_item_box, render_item):

    boxes = {}
    box_separators = {}
    if icon_config.vertical:
        main_box = gtk.VBox()
        box_left = gtk.VBox()
        box = gtk.VBox()
        box_right = gtk.VBox()
        separator_left = gtk.HSeparator()
        separator_right = gtk.HSeparator()
    else:
        main_box = gtk.HBox()
        box_left = gtk.HBox()
        box = gtk.HBox()
        box_right = gtk.HBox()
        separator_left = gtk.VSeparator()
        separator_right = gtk.VSeparator()

    main_icon = render_item(tray.main_item)
    main_icon.show()

    main_box.pack_start(box_left)
    main_box.pack_start(box)
    main_box.pack_start(box_right)

    main_box.show()
    box_left.show()
    box.show()
    box_right.show()

    def separators_changed(tray_config):
        separators = tray_config.separators
        vertical = icon_config.vertical
        if separators & LEFT:
            if separator_left not in box_left.get_children():
                box_left.pack_start(separator_left)
                separator_left.show()
        else:
            if separator_left in box_left.get_children():
                box_left.remove(separator_left)

        if separators & RIGHT:
            if separator_right not in box_right.get_children():
                box_right.pack_end(separator_right)
                separator_right.show()
        else:
            if separator_right in box_right.get_children():
                box_right.remove(separator_right)

    def menus_changed(tray_config):
        menus = tray_config.menus
        old_box, new_box = (
            (box_right, box_left) if menus == LEFT
            else (box_left, box_right)
        )

        if main_icon in old_box.get_children():
            old_box.remove(main_icon)
        if main_icon not in new_box.get_children():
            new_box.pack_end(main_icon)
            main_icon.show_all()

    tray_config_handlers = [
        tray_config.connect(
            "separators-changed", separators_changed
        ),
        tray_config.connect("menus-changed", menus_changed)
    ]

    box_widgets = {}

    def box_added(tray, item_box):
        widget = box_widgets[item_box] = render_item_box(item_box)
        box.pack_start(widget)

    def box_removed(tray, item_box):
        widget = box_wiggets.pop(item_box)
        widget.destroy()

    def destroyed(tray):
        main_box.destroy()

    tray_handlers = [
        tray.connect("box-added", box_added),
        tray.connect("box-removed", box_added),
        tray.connect("destroyed", destroyed),
    ]

    def main_box_destroyed(main_box):
        for handler in tray_config_handlers:
            tray_config.disconnect(handler)
        for handler in tray_handlers:
            tray.disconnect(handler)

    main_box.connect("destroy", main_box_destroyed)

    separators_changed(tray_config)
    menus_changed(tray_config)

    for item_box in tray.boxes:
        box_added(tray, item_box)

    return main_box
