from gi.repository import GObject
from gi.types import GObjectMeta


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


class ConfigMeta(GObjectMeta):

    def __init__(self, name, bases, attrs):
        GObjectMeta.__init__(self, name, bases, attrs)
        for key, attr in attrs.items():
            if not isinstance(attr, Attribute):
                continue
            attr._attr = key
            attr._internal_attr = '_Attribute__' + key
            attr._signal_name = '%s-changed' % key.replace('_', '-')
            GObject.signal_new(
                attr._signal_name, self, GObject.SignalFlags.RUN_FIRST,
                GObject.TYPE_NONE, ()
            )


class Config(GObject.Object, metaclass=ConfigMeta):
    """
    A C{Config} is an object containing attributes. They can be added using the
    L{Attribute} descriptor.
    If an attribute is changed, a signal "<attribute>-changed" is emitted.
    """

    def __init__(self, **attrs):
        """Initialize a Config."""
        GObject.Object.__init__(self)
        for key, value in attrs.items():
            setattr(self, key, value)


GObject.type_register(Config)
