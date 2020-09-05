import inspect


class Function:
    __slots__ = ("__target", "env", "__name__", "__signature", "__parameters")

    def __init__(self, name: str, target):
        if not inspect.isroutine(target):
            raise TypeError("`target` need to be a routine")

        self.__target = target
        if name:
            self.__target.__name__ = name
        else:
            name = target.__name__

        self.env = None

        self.__name__ = name

        self.__signature = inspect.signature(target)
        self.__parameters = self.__signature.parameters

    def __repr__(self):
        return f"<Function {self.__name__}: {self.__target}>"

    def __call__(self, *args, **kwargs):
        converted_args = []
        converted_kwargs = {}

        result = self.__signature.bind(self.env, *args, **kwargs)
        result.apply_defaults()

        for parameter, argument in result.arguments.items():
            parameter = self.__parameters[parameter]
            converter = parameter.annotation

            if converter == inspect._empty:
                converter = lambda x: x

            argument = converter(argument)

            if parameter.kind in [
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD]:
                    converted_args.append(argument)
            elif parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                converted_args.extend(argument)
            elif parameter.kind == inspect.Parameter.VAR_KEYWORD:
                converted_kwargs.update(argument)
            else:
                converted_kwargs[parameter.name] = argument

        return self.__target(*converted_args, **converted_kwargs)

def function(name: str=None):
    def decorator(func):
        return Function(name, func)
    return decorator


class Attribute:
    """
    ...

    Notes
    -----
    You don't need create manually .;;

    Attributes
    ----------
    call : str
        ...
    """
    __slots__ = ("call", "env", "__target", "__cache")

    def __init__(self, call: str, target, *, constant: bool=True):
        self.call = call
        self.env = None

        if constant:
            self.__cache = target()
        else:
            self.__target = target

        
    def __call__(self):
        try:
            return self.__cache
        except AttributeError:
            return self.__target(self.env)

    @property
    def is_constant(self) -> bool:
        """..."""
        try:
            self.__cache
        except AttributeError:
            return False
        return True

def attribute(call: str=None, *, is_constant: bool=True):
    """
    -> Decorator
    ...
    
    Parameters
    ----------
    call : str (None)
        ...
    is_constant : bool (True)
        ...
    """
    call = call or function.__name__
    def decorator(function):
        attribute = Attribute(call, function, constant=is_constant)
        return attribute
    return decorator


class Environment:
    """
    Examples
    --------
    ```
    class Base(macroma.Environment):
        @macroma.function(name="hello")
        def hello_function(self, macroma):
            print("Hello, world!")

        @macroma.attribute(call="RandomNumber", is_constant=False)
        def random_number(self, macroma):
            return random.randint(1, 10)

    print(Base)
    ```
    """        
    __slots__ = ("name", "macroma", "__attributes", "__functions")

    def __init__(self, macroma):
        self.macroma = macroma

        self.__attributes = {}
        self.__functions = {}

        for _, member in inspect.getmembers(self):
            if isinstance(member, Attribute):
                member.env = self
                self.__attributes[member.call] = member
            elif isinstance(member, Function):
                member.env = self
                self.__functions[member.__name__] = member

    @property
    def attributes(self) -> dict:
        return self.__attributes

    @property
    def functions(self) -> dict:
        return self.__functions
