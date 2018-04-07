from gi.repository import Gtk, Gdk, GObject

from traylib import TARGET_MOZ_URL, TARGET_URI_LIST

_targets = [
    Gtk.TargetEntry.new("text/uri-list", 0, TARGET_URI_LIST),
    Gtk.TargetEntry.new("text/x-moz-url", 0, TARGET_MOZ_URL),
]


def render_item_box(item_box, icon_config, render_item, item_from_uri):
    """
    Render an item box to a C{Gtk.Box}.

    @param item_box: The L{ItemBox} to render.
    @param icon_config: The L{IconConfig} configuring the icons.
    @param render_item: Callable called with an L{Item} to render it.
    @param item_from_uri: Callable for creating an L{Item} from a URI dragged
        to the item box.

    @return: The managed C{Gtk.Box}.
    """

    if icon_config.vertical:
        box = Gtk.VBox()
    else:
        box = Gtk.HBox()

    item_widgets = {}

    class state:
        drag_source_item = None
        spring_open_event = 0
        dropped_uris = None
        has_new_item = False

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
            state.dropped_uris = None
            state.has_new_item = False

        def drag_drop(widget, context, data, info, time):
            #target = widget.drag_dest_find_target(context, _targets)
            #widget.drag_get_data(context, target, time)
            if state.dropped_uris:
                item.uris_dropped(state.dropped_uris, context.action)
                context.drop_finish(True, time)
            state.dropped_uris = None
            return True

        def drag_leave(widget, context, time):
            if state.spring_open_event != 0:
                GObject.source_remove(state.spring_open_event)
                state.spring_open_event = 0

        def start_spring_open(context, time):
            if state.spring_open_event == 0:
                state.spring_open_event = GObject.timeout_add(
                    1000, spring_open, time
                )
            if item.is_drop_target():
                action = context.suggested_action
            else:
                action = 0
            Gdk.drag_status(context, action, time)

        def drag_data_received(widget, context, x, y, data, info, time):
            if data.get_data() is None:
                context.drop_finish(False, time)
                return
            if Gtk.drag_get_source_widget(context) is widget:
                return
            state.dropped_uris = []
            if info == TARGET_MOZ_URL:
                state.dropped_uris = [
                    data.get_data().decode('utf-16')
                    .encode('utf-8').split('\n')[0]
                ]
            elif info == TARGET_URI_LIST:
                state.dropped_uris = data.get_uris()
            for uri in state.dropped_uris:
                new_item = item_from_uri(uri)
                if new_item is not None:
                    item_box.add_item(new_item)
                    state.drag_source_item = new_item
                    state.has_new_item = True
                    Gdk.drag_status(context, 0, time)
                    #drag_motion(widget, context, x, y, time)
                    break
            else:
                start_spring_open(context, time)
                #return True
            #item.uris_dropped(uri_list, context.action)
            #context.drop_finish(True, time)

        def drag_motion(widget, context, x, y, time):
            if state.drag_source_item is item:
                return False
            if state.drag_source_item is None:
                if state.dropped_uris:
                    start_spring_open(context, time)
                else:
                    target = widget.drag_dest_find_target(
                        context, Gtk.TargetList.new(_targets)
                    )
                    widget.drag_get_data(context, target, time)
                return True
            else:
                if icon_config.locked and not state.has_new_item:
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
                Gdk.drag_status(context, 0, time)
                return True
            return False

        def leave_notify_event(widget, event):
            state.drag_source_item = None
            state.has_new_item = False
            state.dropped_uris = None
        widget.drag_dest_set(
            Gtk.DestDefaults.HIGHLIGHT, _targets, Gdk.DragAction.DEFAULT
        )
        widget.connect("drag-begin", drag_begin)
        widget.connect("drag-end", drag_end)
        widget.connect("drag-leave", drag_leave)
        widget.connect("drag-motion", drag_motion)
        widget.connect("drag-drop", drag_drop)
        widget.connect("drag-data-received", drag_data_received)
        widget.connect("leave-notify-event", leave_notify_event)
        box.pack_start(widget, True, True, 0)

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
