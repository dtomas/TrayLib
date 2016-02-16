import gobject


class Attribute(object):
    """Descriptor adding an attribute to a L{Config} class."""

    # These are set by ConfigMeta.
    _attr = None
    _internal_attr = None
    _signal_name = None

    def __init__(self, default=None):
        self._default = default

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return getattr(obj, self._internal_attr)
        except AttributeError:
            return self._default

    def __set__(self, obj, value):
        setattr(obj, self._internal_attr, value)
        obj.emit(self._signal_name)


class ConfigMeta(gobject.GObjectMeta):

    def __init__(self, name, bases, attrs):
        gobject.GObjectMeta.__init__(self, name, bases, attrs)
        for key, attr in attrs.iteritems():
            if not isinstance(attr, Attribute):
                continue
            attr._attr = key
            attr._internal_attr = '_Attribute__' + key
            attr._signal_name = '%s-changed' % key.replace('_', '-')
            gobject.signal_new(
                attr._signal_name, self, gobject.SIGNAL_RUN_FIRST,
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
        for key, value in attrs.iteritems():
            setattr(self, key, value)


gobject.type_register(Config)
