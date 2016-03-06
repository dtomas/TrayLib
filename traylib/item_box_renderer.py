import gtk
import gobject

from traylib import TARGET_MOZ_URL, TARGET_URI_LIST

_targets = [
    ("text/uri-list", 0, TARGET_URI_LIST),
    ("text/x-moz-url", 0, TARGET_MOZ_URL),
]


def render_item_box(item_box, icon_config, render_item):
    """
    Render an item box to a C{gtk.Box}.

    @param item_box: The L{ItemBox} to render.
    @param icon_config: The L{IconConfig} configuring the icons.
    @param render_item: Callable called with an L{Item} to render it.

    @return: The managed C{gtk.Box}.
    """

    if icon_config.vertical:
        box = gtk.VBox()
    else:
        box = gtk.HBox()

    item_widgets = {}

    class state:
        drag_source_item = None
        spring_open_event = 0

    def item_added(item_box, item):
        widget = item_widgets[item] = render_item(item)

        def spring_open(time):
            if item.spring_open(time):
                return True
            else:
                state.spring_open_event = 0
                return False

        def drag_begin(widget, context):
            state.drag_source_item = item

        def drag_end(widget, context):
            state.drag_source_item = None

        def drag_drop(widget, context, data, info, time):
            target = widget.drag_dest_find_target(context, _targets)
            widget.drag_get_data(context, target, time)
            return True

        def drag_leave(widget, context, time):
            if state.spring_open_event != 0:
                gobject.source_remove(state.spring_open_event)
                state.spring_open_event = 0

        def drag_data_received(widget, context, x, y, data, info, time):
            if data.data is None:
                context.drop_finish(False, time)
                return
            if context.get_source_widget() is widget:
                return
            uri_list = []
            if info == TARGET_MOZ_URL:
                uri_list = [
                    data.data.decode('utf-16').encode('utf-8').split('\n')[0]
                ]
            elif info == TARGET_URI_LIST:
                uri_list = data.get_uris()
            item.uris_dropped(uri_list, context.action)
            context.drop_finish(True, time)

        def drag_motion(widget, context, x, y, time):
            if state.drag_source_item is item:
                return False
            if state.drag_source_item is None:
                if state.spring_open_event == 0:
                    state.spring_open_event = gobject.timeout_add(
                        1000, spring_open, time
                    )
                if item.is_drop_target():
                    action = context.suggested_action
                else:
                    action = 0
                context.drag_status(action, time)
                return True
            else:
                if icon_config.locked:
                    return False
                source_item_position = item_box.items.index(
                    state.drag_source_item
                )
                item_position = item_box.items.index(item)
                rect = widget.get_allocation()
                if icon_config.vertical:
                    center = rect.height / 2
                    if (source_item_position < item_position and y > center or
                            source_item_position > item_position and
                            y < center):
                        item_box.reorder_item(
                            state.drag_source_item, item_position
                        )
                    else:
                        return False
                else:
                    center = rect.width / 2
                    if (source_item_position < item_position and x > center or
                            source_item_position > item_position and
                            x < center):
                        item_box.reorder_item(
                            state.drag_source_item, item_position
                        )
                    else:
                        return False
                context.drag_status(0, time)
                return True
            return False
        widget.drag_dest_set(
            gtk.DEST_DEFAULT_HIGHLIGHT, _targets, gtk.gdk.ACTION_DEFAULT
        )
        widget.connect("drag-begin", drag_begin)
        widget.connect("drag-end", drag_end)
        widget.connect("drag-leave", drag_leave)
        widget.connect("drag-motion", drag_motion)
        widget.connect("drag-drop", drag_drop)
        widget.connect("drag-data-received", drag_data_received)
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
