from traylib.handler import AbstractHandler


class Handlers(AbstractHandler):

    def __init__(self, item_class):
        AbstractHandler.__init__(self)
        self.__handlers = {}
        self.__watchers = set()
        self.__item_class = item_class

    def add_watcher(self, watcher):
        self.__watchers.add(watcher)
        for item_id, handlers in self.__handlers.iteritems():
            watcher.item_added(self.__item_class(item_id), handlers)

    def remove_watcher(self, watcher):
        self.__watchers.remove(watcher)

    def _add_item(self, item_id):
        if not item_id:
            return None
        #print "item %s added" % item_id
        item = self.__item_class(item_id)
        handlers = self.get_handlers_for(item)
        #print "handlers: %s" % str(handlers)
        if not handlers:
            return None
        self.__handlers[item_id] = handlers
        for watcher in self.__watchers:
            watcher.item_added(item, handlers)
        return item

    def _remove_item(self, item_id):
        if not item_id:
            return
        #print "item %s removed" % item_id
        handlers = self.__handlers.get(item_id)
        #print "handlers: %s" % str(handlers)
        if not handlers:
            return
        for watcher in self.__watchers:
            watcher.item_removed(self.__item_class(item_id))
        #print "clearing states"
        for handler in handlers:
            handler._clear_state(item_id)
        del self.__handlers[item_id]

    def _update_handlers(self, item):
        assert item.id in self.__handlers
        handlers = self.get_handlers_for(item)
        #print "handlers: %s" % handlers
        item_id = item.id
        if item_id in self.__handlers:
            if handlers:
                old_handlers = set(self.__handlers[item_id])
                handlers = set(handlers)
                added_handlers = handlers - old_handlers
                removed_handlers = old_handlers - handlers
                self.__handlers[item_id] = handlers
                for watcher in self.__watchers:
                    watcher.handlers_added(item, added_handlers)
                    watcher.handlers_removed(item, removed_handlers)
            else:
                del self.__handlers[item_id]
                for watcher in self.__watchers:
                    watcher.item_removed(item, handlers)
        elif handlers:
            self.__handlers[item_id] = handlers
            for watcher in self.__watchers:
                watcher.item_added(item)

    def get_handlers(self, item):
        return self.__handlers[item.id]

    def options_changed(self):
        for handler in self.subhandlers:
            handler.options_changed()
