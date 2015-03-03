import gtk, os, sys, imp
from rox.options import Option
from traylib import ICON_THEME


class Handler(object):
    __handlers = {}

    def __new__(cls, *args, **kwargs):
        handler = Handler.__handlers.get(cls.__name__)
        if handler:
            return handler
        handler = object.__new__(cls)
        return handler

    def __init__(self):
        if Handler.__handlers.get(self.__class__.__name__):
            return # handler has already been initialized
        object.__init__(self)
        self.__config = None
        self.__icons = {}
        self.__subhandlers = None
        self.__module_dir = os.path.dirname(sys.modules[self.__module__].__file__)
        icon_dir = os.path.join(self.__module_dir, 'icons')
        if os.path.isdir(icon_dir):
            ICON_THEME.append_search_path(icon_dir)
        self.__options = {}
        module_name = self.__module__
        for key, default in self.make_options().iteritems():
            self.__options[key] = Option("%s.%s" % (module_name, key), default)
        Handler.__handlers[self.__class__.__name__] = self

    def get_option(self, key):
        option = self.__options.get(key)
        if not option:
            return None
        return option.value

    def make_options(self):
        return {}

    def _clear_state(self, id):
        state = self.get_state(id)
        if not state:
            return
        self.removed(state)
        state.destroy()

    def get_state(self, item_id):
        state_class = self.state_class
        if not state_class:
            return None
        state = state_class.get(item_id)
        return state

    def options_changed(self):
        pass 

    def get_subhandlers(self):
        if self.__subhandlers == None:
            self.__subhandlers = self.__make_subhandlers()
        return self.__subhandlers

    def __make_subhandlers(self):
        handlers = []
        module_name = self.__module__
        handler_path = self.__module_dir
        for dirname in os.listdir(handler_path):
            path = os.path.join(self.__module_dir, dirname)
            if not os.path.isdir(path):
                continue
            name = module_name + '.' + dirname
            package = imp.load_package(name, path)
            if not hasattr(package, 'create_handler'):
                continue
            handler = package.create_handler()
            handlers.append(handler)
        return handlers

    def get_handlers_for(self, item):
        if not self.handles(item):
            return []
        handlers = []
        if not self.is_abstract():
            handlers.append(self)
        for handler in self.subhandlers:
            handlers += handler.get_handlers_for(item)
        state = self.get_state(item)
        #print "state: %s" % state
        if not handlers:
            if state:
                state.destroy(item.id)
        else:
            state_class = self.state_class
            if not state and state_class:
                state_class(item)
        return handlers

    def get_handler_icon(self, size):
        icon = self.__icons.get(size)
        if icon:
            return icon
        for icon_name in self.icon_names:
            icon_info = ICON_THEME.lookup_icon(icon_name, size, 0)
            if not icon_info:
                continue
            icon = gtk.gdk.pixbuf_new_from_file(icon_info.get_filename())
            #if icon.get_width() != size:
            #    icon = icon.scale_simple(size,size, gtk.gdk.INTERP_BILINEAR)
            self.__icons[size] = icon
            #icon_info.free()
            return icon
        return None

    #def get_state(self, device):
    #    state_class = self.state_class
    #    if not state_class:
    #        return None
    #    return state_class.get_state(device)

    def get_state_class(self):
        return None

    def get_icon_updater_class(self):
        return None

    def get_handler_icon_names(self):
        return []

    def get_name(self):
        return ""

    def handles(self, obj):
        return True

    def is_abstract(self):
        return False

    def get_priority(self):
        return 0

    def get_icon_path(self, state):
        return None

    def get_icon_names(self, state):
        return []
    
    def get_menu_items(self, state):
        return []

    def removed(self, state):
        pass

    def make_emblem(self, state):
        return None

    def make_name(self, state):
        return None

    def should_have_window(self, state, window):
        return False

    icon_names = property(lambda self : self.get_handler_icon_names())
    icon_updater_class = property(lambda self : self.get_icon_updater_class())
    module_dir = property(lambda self : self.__module_dir)
    name = property(lambda self : self.get_name())
    priority = property(lambda self : self.get_priority())
    state_class = property(lambda self : self.get_state_class())
    subhandlers = property(lambda self : self.get_subhandlers())


class AbstractHandler(Handler):
    def is_abstract(self):
        return True
