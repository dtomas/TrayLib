

class Attribute(object):
    """Descriptor adding an attribute to a L{Config} class."""

    # This is set by ConfigMeta.
    _attr = None

    def __init__(self, update_func=None, default=None):
        self._default = default
        self._update_func = update_func

    def _ensure_attribute(self, obj):
        if obj.has_attribute(self._attr):
            return
        obj.add_attribute(
            self._attr,
            self._default,
            self._update_func if self._update_func is not None
            else 'update_option_%s' % self._attr,
        )

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        self._ensure_attribute(obj)
        return obj.get_attribute(self._attr)

    def __set__(self, obj, value):
        self._ensure_attribute(obj)
        obj.set_attribute(self._attr, value)


class ConfigMeta(type):

    def __init__(self, name, bases, attrs):
        type.__init__(self, name, bases, attrs)
        for key, attr in attrs.iteritems():
            if not isinstance(attr, Attribute):
                continue
            attr._attr = key


class Config(object):
    """
    A C{Config} is an object containing attributes. They can be added using the 
    L{add_attribute()} method, changed using L{set_attribute()} and accessed
    using L{get_attribute()}.
    If an attribute is changed, an update function is called on all
    configurable objects registered via L{add_configurable()}.
    """

    __metaclass__ = ConfigMeta

    def __init__(self, **attrs):
        """
        Creates a new C{Config}.
        """
        self.__attributes = {}
        self.__objects = []
        for key, value in attrs.iteritems():
            setattr(self, key, value)

    def has_attribute(self, key):
        """
        Returns C{True} if the object has an attribute of the given name.

        @param key: The key.
        """
        return key in self.__attributes

    def add_attribute(self, key, value, update_func=None):
        """
        Adds an attribute to the C{Config}.
        
        @param key: The key.
        @param value: The value.
        @param update_func: The name of a method that gets called on all 
            configurable objects (registered via L{add_configurable()}) when
            the value of the attribute has changed.
        """
        self.__attributes[key] = value, update_func

    def set_attribute(self, key, value):
        """
        Sets the attribute identified by C{key} to the value C{value}.
        
        @param key: The key.
        @param value: The new value. 
        """
        assert key in self.__attributes

        old_value, update_func = self.__attributes[key]
        if old_value == value:
            return
        self.__attributes[key] = value, update_func

        if update_func:
            for obj in self.__objects:
                if hasattr(obj, update_func):
                    getattr(obj, update_func)()

    def get_attribute(self, key):
        """
        @param key: The key.
        @return: The value associated with the given C{key}.
        """
        value, _update_func = self.__attributes[key]
        return value

    def add_configurable(self, obj):
        """
        Registers a configurable object.

        @param obj: The object.
        """
        self.__objects.append(obj)

    def remove_configurable(self, obj):
        """
        Unregisters a configurable object.

        @param obj: The object.
        """
        self.__objects.remove(obj)

    def has_configurable(self, obj):
        """
        @param obj: The configurable object.
        @return: C{True} if the configurable object is registered with the 
            C{Config}.
        """
        return obj in self.__objects
    
    attributes = property(lambda self : self.__attributes.keys())
