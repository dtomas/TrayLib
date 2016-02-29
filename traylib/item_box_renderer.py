import gtk


def render_item_box(item_box, icon_config, render_item):

    if icon_config.vertical:
        box = gtk.VBox()
        separator = gtk.HSeparator()
    else:
        box = gtk.HBox()
        separator = gtk.VSeparator()

    item_widgets = {}

    def item_added(item_box, item):
        widget = item_widgets[item] = render_item(item)
        box.pack_start(widget)
        widget.show()

    def item_removed(item_box, item):
        try:
            widget = item_widgets.pop(item)
        except KeyError:
            return
        widget.destroy()

    def destroyed(item_box):
        box.destroy()

    item_box.connect("item-added", item_added)
    item_box.connect("item-removed", item_removed)
    item_box.connect("destroyed", destroyed)

    for item in item_box.items:
        item_added(item_box, item)

    box.show()

    return box
