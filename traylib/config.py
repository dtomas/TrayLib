

class Config(object):
    """
    A C{Config} is an object containing attributes. They can be added using the 
    L{add_attribute()} method, changed using L{set_attribute()} and accessed
    using L{get_attribute()}.
    If an attribute is changed, an update function is called on all
    configurable objects registered via L{add_configurable()}.
    """

    def __init__(self):
        """
        Creates a new C{Config}.
        """
        self.__attributes = {}
        self.__objects = []

    def add_attribute(self, key, value, update_func=None, set_func=None):
        """
        Adds an attribute to the C{Config}.
        
        @param key: The key.
        @param value: The value.
        @param update_func: The name of a method that gets called on all 
            configurable objects (registered via L{add_configurable()}) when
            the value of the attribute has changed.
        @param set_func: The name of a method with signature 
            C{set_func(old_value, new_value)} that gets called on the C{Config} 
            when the value of the attribute has changed.
        """
        self.__attributes[key] = (value, update_func, set_func)
        if set_func:
            getattr(self, set_func)(None, value)

    def set_attribute(self, key, value):
        """
        Sets the attribute identified by C{key} to the value C{value}.
        
        @param key: The key.
        @param value: The new value. 
        """
        assert key in self.__attributes

        old_value, update_func, set_func = self.__attributes[key]
        if old_value == value:
            return
        self.__attributes[key] = (value, update_func, set_func)
        if set_func:
            getattr(self, set_func)(old_value, value)

        if update_func:
            for obj in self.__objects:
                if hasattr(obj, update_func):
                    getattr(obj, update_func)()

    def get_attribute(self, key):
        """
        @param key: The key.
        @return: The value associated with the given C{key}.
        """
        value, update_func, set_func = self.__attributes[key]
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
