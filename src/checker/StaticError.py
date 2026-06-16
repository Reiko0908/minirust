class StaticError(Exception):
    pass

class Redeclared(StaticError):
    def __init__(self, kind: str, name: str):
        self.kind = kind
        self.name = name
    def __str__(self):
        return f"Redeclared({self.kind}, {self.name})"

class UndeclaredIdentifier(StaticError):
    def __init__(self, name: str):
        self.name = name
    def __str__(self):
        return f"UndeclaredIdentifier({self.name})"

class UndeclaredFunction(StaticError):
    def __init__(self, name: str):
        self.name = name
    def __str__(self):
        return f"UndeclaredFunction({self.name})"

class UndeclaredStruct(StaticError):
    def __init__(self, name: str):
        self.name = name
    def __str__(self):
        return f"UndeclaredStruct({self.name})"

class TypeCannotBeInferred(StaticError):
    def __init__(self, ctx):
        self.ctx = ctx
    def __str__(self):
        return f"TypeCannotBeInferred({self.ctx})"

class TypeMismatchInStatement(StaticError):
    def __init__(self, stmt):
        self.stmt = stmt
    def __str__(self):
        return f"TypeMismatchInStatement({self.stmt})"

class TypeMismatchInExpression(StaticError):
    def __init__(self, expr):
        self.expr = expr
    def __str__(self):
        return f"TypeMismatchInExpression({self.expr})"

class MustInLoop(StaticError):
    def __init__(self, stmt):
        self.stmt = stmt
    def __str__(self):
        return f"MustInLoop({self.stmt})"

class CannotAssignToConstant(StaticError):
    def __init__(self, expr):
        self.expr = expr
    def __str__(self):
        return f"CannotAssignToConstant({self.expr})"
