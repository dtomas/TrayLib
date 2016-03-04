import gtk

import traylib


def render_item_box(item_box, icon_config, render_item):

    if icon_config.vertical:
        box = gtk.VBox()
    else:
        box = gtk.HBox()

    item_widgets = {}

    def item_added(item_box, item):
        widget = item_widgets[item] = render_item(item)

        def drag_motion(widget, context, x, y, time):
            source_widget = context.get_source_widget()
            if source_widget is None:
                source_widget = traylib.drag_source_widget
            if source_widget is widget:
                return False
            for source_item in item_box.items:
                if item_widgets[source_item] is source_widget:
                    break
            else:
                # Source widget not in item box.
                return False
            source_item_position = item_box.items.index(source_item)
            item_position = item_box.items.index(item)
            rect = widget.get_allocation()
            center = rect.width / 2
            if (source_item_position < item_position and x > center or
                    source_item_position > item_position and x < center):
                position = item_position
            else:
                return False
            item_box.reorder_item(source_item, position)
            context.drag_status(0, time)
            return True
        widget.connect("drag-motion", drag_motion)
        box.pack_start(widget)

    def item_removed(item_box, item):
        try:
            widget = item_widgets.pop(item)
        except KeyError:
            return
        widget.destroy()

    def item_reordered(item_box, item, position):
        widget = item_widgets[item]
        box.reorder_child(widget, position)

    def destroyed(item_box):
        box.destroy()

    item_box.connect("item-added", item_added)
    item_box.connect("item-removed", item_removed)
    item_box.connect("item-reordered", item_reordered)
    item_box.connect("destroyed", destroyed)

    for item in item_box.items:
        item_added(item_box, item)

    box.show()

    return box
