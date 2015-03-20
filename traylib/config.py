import gobject


class Attribute(object):
    """Descriptor adding an attribute to a L{Config} class."""

    # These are set by ConfigMeta.
    _attr = None
    _internal_attr = None

    def __init__(self, update_func=None, default=None):
        self._default = default
        self._update_func = update_func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return getattr(obj, self._internal_attr)
        except AttributeError:
            return self._default

    def __set__(self, obj, value):
        setattr(obj, self._internal_attr, value)
        if self._update_func is None:
            self._update_func = 'update_option_%s' % self._attr
        for configurable in obj.get_configurables():
            try:
                update = getattr(configurable, self._update_func)
            except AttributeError:
                continue
            update()


class ConfigMeta(gobject.GObjectMeta):

    def __init__(self, name, bases, attrs):
        gobject.GObjectMeta.__init__(self, name, bases, attrs)
        for key, attr in attrs.iteritems():
            if not isinstance(attr, Attribute):
                continue
            attr._attr = key
            attr._internal_attr = '_Attribute__' + key
            gobject.signal_new(
                "%s-changed" % key, self, gobject.SIGNAL_RUN_FIRST,
                gobject.TYPE_NONE, ()
            )


class Config(gobject.GObject):
    """
    A C{Config} is an object containing attributes. They can be added using the 
    L{Attribute} descriptor.
    If an attribute is changed, an update function is called on all
    configurable objects registered via L{add_configurable()}.
    """

    __metaclass__ = ConfigMeta

    def __init__(self, **attrs):
        """
        Creates a new C{Config}.
        """
        gobject.GObject.__init__(self)
        self.__objects = set()
        for key, value in attrs.iteritems():
            setattr(self, key, value)

    def add_configurable(self, obj):
        """
        Registers a configurable object.

        @param obj: The object.
        """
        self.__objects.add(obj)

    def remove_configurable(self, obj):
        """
        Unregisters a configurable object.

        @param obj: The object.
        """
        try:
            self.__objects.remove(obj)
        except KeyError:
            # Already removed.
            pass

    def has_configurable(self, obj):
        """
        @param obj: The configurable object.
        @return: C{True} if the configurable object is registered with the 
            C{Config}.
        """
        return obj in self.__objects

    def get_configurables(self):
        return self.__objects


gobject.type_register(Config)
