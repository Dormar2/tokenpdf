from __future__ import annotations
from typing import Any
from .general import parent_class_leading_to

class Registry:
    """
    A simple registry class that allows for registering and getting items by name.
    """
    def __init__(self):
        self._items = {}
    
    def register(self, name, item):
        if isinstance(name, tuple|list):
            for n in name:
                self.register(n, item)
            return
        self._items[name] = item
    
    def get(self, name):
        return self._items[name]
    
    def __getitem__(self, name):
        return self.get(name)
    
    def __setitem__(self, name, item):
        self.register(name, item)

    def __contains__(self, name):
        return name in self._items
    
    def __iter__(self):
        return iter(self._items)
        

class RegistryClass:
    """
    A metaclass that allows for making "classes with a registry",
    where the registry is for subclasses of the class.

    To use, define the class with the registry as:
    ```class MyParentClass(RegistryClass):
        pass```
    
    Then you can name subclasses as:
    ```class MySubclass(MyParentClass, name="myname"):
        pass```
        
    Then accessing by:
    ```MyParentClass.get_registry()["myname"]```

    If you don't specify a name, the subclass will have its own registry.
    If you don't specify a name for a sub-sub class, it will share the registry with its parent,
    unless `dedicated` is set to True.

    Another option is to use the global registry. To do this, define the class as:
    ```class MyParentClass(RegistryClass, glob=True):
        pass```
    
    Then you can name subclasses as:
    ```class MySubclass(name="myname"):
        pass```
        
    Then accessing the global registry by:
    ```global_registry["myname"]```

    You also don't have to subclass, you can register a class in the global registry by:
    ```class MyClass(RegistryClass, name="myname", glob=True):
        pass```

    When accessing a registry, the returned data is either the registered class,
    or a tuple of the registered class and the returned value from the class method _get_class_registry_args(name)
    @see _get_class_registry_args
    

    The class also provides a decorator for registering classes, or class-like functions.
    @see register
    """
    def __init_subclass__(cls, 
                        glob:bool = False,
                        name:str = None, 
                        dedicated:bool = False,
                        **kwargs):
        super().__init_subclass__(**kwargs)
        RegistryClass._initialize_class_registry()
        cls.__register_subclass(cls, glob, name, dedicated)

    @staticmethod
    def __register_subclass(cls, glob, name, dedicated):
        if isinstance(name, tuple|list):
            for n in name:
                cls.__register_subclass(cls, glob, n, dedicated)
            return
        if glob: 
            # For the global repository
            if not name:
                name = cls.__name__.lower()
            RegistryClass.get_registry()[name] = cls
            return
        if name is None:
            if cls.has_non_global_registry() and not dedicated:
                # Nothing to do
                return
            cls._initialize_class_registry()
        else:
            args = cls._get_class_registry_args(name)
            item = (cls, args) if args is not None else cls
            cls.get_registry()[name] = item

    @classmethod
    def get_registry(cls):
        if cls is RegistryClass:
            cls._initialize_class_registry()
        rname = cls._registry_name()
        if hasattr(cls, rname):
            return getattr(cls, rname)
        return parent_class_leading_to(cls, RegistryClass).get_registry()
    
    @classmethod
    def has_own_registry(cls):
        return hasattr(cls, cls._registry_name())
    
    @classmethod
    def has_parent_registry(cls):
        if cls is RegistryClass:
            return False
        return parent_class_leading_to(cls, RegistryClass).has_own_registry()

    @classmethod
    def has_non_global_registry(cls):
        return cls.get_registry() is not global_registry

    @classmethod
    def _registry_name(cls):
        return f"__registry_{cls.__name__}"

    @classmethod
    def _initialize_class_registry(cls):
        rname = cls._registry_name()
        if not hasattr(cls, rname):
            setattr(cls, rname, Registry())
    """
    An overridable method that returns additional arguments for the registry.
    If None is returned, the class is registered as is.

    Args:
        name: The name argument of the class being registered
    """
    @classmethod
    def _get_class_registry_args(cls, name) -> Any | None:
        return None
    

    @classmethod
    def register(cls, *args, name = None, **kwargs) -> RegisterClassRegistryDecorator | None:
        """
        Either registers an item in this class's registry,
        or returns a decorator that registers its argument.
        Item cannot be a string!
        """
        if len(args) == 0:
            item_or_name = None
        else:
            item_or_name = args[0]
        names = list(args[1:])
        if name is not None:
            names.append(name)
        if isinstance(item_or_name, str):
            names.insert(0,item_or_name)
            return RegisterClassRegistryDecorator(name=names, **kwargs, registry_class=cls)
        item = item_or_name
        if not names:
            names.append(item.__name__.lower())
        cls.get_registry().register(names, item)
        

class RegisterClassRegistryDecorator:
    def __init__(self, registry_class, name = None, **kwargs):
        self.name = name
        self.registry_class = registry_class
        self.kwargs = kwargs

    def __call__(self, item):
        c = self.registry_class
        name = self.name if self.name else item.__name__.lower()
        c.get_registry()[name] = item if not self.kwargs else (item, self.kwargs)
        return item

global_registry = RegistryClass.get_registry()
register_global = RegistryClass.register