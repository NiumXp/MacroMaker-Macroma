class EnvironmentNotFoundError(Exception):
    def __init__(self, name: str):
        super().__init__(f"{name} environment not found")


class FunctionNotFoundError(Exception):
    def __init__(self, name: str):
        super().__init__(f"{name} function not found")


class AttributeNotFoundError(Exception):
    def __init__(self, name: str):
        super().__init__(f"{name} attribute not found")
