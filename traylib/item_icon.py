import gtk, os, sys
from traylib.item import Item
from traylib.winicon import WinIcon


class ItemIcon(WinIcon):
    
    __icons = {}

    @classmethod
    def class_options_changed(cls):
        for icon in ItemIcon.__icons.get(cls, []):
            icon.options_changed()

    def __new__(cls, icon_config, win_config, device):
        """
        Creates a new C{ItemIcon}.
        @param device: the L{Item} the icon represents 
        """
        icon = WinIcon.__new__(cls)
        cls.__icons.setdefault(cls, []).append(icon) 
        return icon

    def __init__(self, icon_config, win_config, item):
        """
        Initializes the C{ItemIcon}.
        
        @param device: the L{Item} the icon represents 
        """
        assert isinstance(item, Item)
        
        WinIcon.__init__(self, icon_config, win_config)
        self.__class__.__module_dir = os.path.dirname(sys.modules[self.__module__].__file__)
        self.__item = item
        self.__handlers = []
        self.__updaters = {}
        
        self.connect("destroy", self.__destroy)

    def __destroy(self, widget):
        assert widget == self
        ItemIcon.__icons.get(self.__class__).remove(self)

    def make_visibility(self):
        return True
    
    def options_changed(self):
        pass
    
    def add_handler(self, handler):
        #print "add handler %s to icon %s" % (handler, self.item.id)
        handlers = self.__handlers
        ##print handlers
        if handler in handlers:
            return
        if not handlers:
            handlers.append(handler)
        else:
            i = 0
            last_index = len(handlers)-1
            for handler2 in handlers:
                if handler.priority > handler2.priority:
                    self.__handlers.insert(i, handler)
                    break
                elif i == last_index:
                    self.__handlers.append(handler)
                i += 1
        state_class = handler.state_class
        #print "state class: %s" % state_class
        if state_class:
            state = handler.state_class(self.item)
            #print "state: %s" % state_class
            updater_class = handler.icon_updater_class
            #print "updater_class: %s" % updater_class
            if updater_class:
                updater = updater_class(self)
                #print "updater: %s" % updater
                state.add_configurable(updater)
                self.__updaters[handler] = updater
        self.update_name()
        self.update_tooltip()
        self.update_visibility()
        self.update_emblem()
        self.update_icon()
        self.update_is_drop_target()
        ##print handlers

    def remove_handler(self, handler):
        if handler not in self.__handlers:
            return
        state_class = handler.state_class
        if state_class:
            state = state_class(self.item)
            handler.removed(state)
            if handler in self.__updaters:
                del self.__updaters[handler]
                state.remove_configurable(updater)
            state.remove()
        self.__handlers.remove(handler)
        self.update_name()
        self.update_tooltip()
        self.update_visibility()
        self.update_emblem()
        self.update_icon()
        self.update_is_drop_target()

    def get_handler_and_state(self, handler_class):
        item_id = self.item.id
        for handler in self.__handlers:
            if isinstance(handler, handler_class):
                return handler, handler.get_state(item_id)
        return None, None

    def click(self, time = 0L):
        menu_items = []
        for handler, state in self.__get_handlers_and_states():
            menu_items = handler.get_menu_items(state) + menu_items
            if menu_items:
                menu_items[len(menu_items)-1].activate()
                return
            
    def get_menu_right(self):
        menu = WinIcon.get_menu_right(self)
        if menu:
            menu.prepend(gtk.SeparatorMenuItem())
            menu.prepend(gtk.SeparatorMenuItem())
        else:
            menu = gtk.Menu()

        menu_items = []
        for handler, state in self.__get_handlers_and_states():
            handler_menu_items = handler.get_menu_items(state)
            if handler_menu_items:
                menu_items = [gtk.SeparatorMenuItem()] + handler_menu_items + menu_items
        #print menu_items

        for menu_item in menu_items:
            menu.prepend(menu_item)

        return menu
    
    def __get_handlers_and_states(self):
        item_id = self.item.id
        for handler in self.__handlers:
            yield handler, handler.get_state(item_id)

    # methods from WinIcon

    def menu_has_kill(self):
        return False

    def should_hide_if_no_visible_windows(self):
        return False
    

    # methods from Icon

    def get_icon_names(self):
        icon_names = []
        for handler, state in self.__get_handlers_and_states():
            handler_icon_names = handler.get_icon_names(state)
            if handler_icon_names:
                icon_names += handler_icon_names
        return icon_names

    def get_icon_path(self):
        for handler, state in self.__get_handlers_and_states():
            icon_path = handler.get_icon_path(state)
            if icon_path:
                return icon_path
        return None

    def make_emblem(self):
        for handler, state in self.__get_handlers_and_states():
            emblem = handler.make_emblem(state)
            if emblem:
                return emblem
        return None
    
    def make_name(self):
        names = []
        for handler, state in self.__get_handlers_and_states():
            name = handler.make_name(state)
            if name:
                if not names:
                    names = [name]
                else:
                    names += ['\n', name]
        return "".join(names)
    
    def should_have_window(self, window):
        for handler, state in self.__get_handlers_and_states():
            if handler.should_have_window(state, window):
                return True
        return False

    item = property(lambda self : self.__item)
    handlers = property(lambda self : self.__handlers)
