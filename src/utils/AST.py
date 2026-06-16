from abc import ABC

class AST(ABC):
    def __eq__(self, other):
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return self.__str__()

    def accept(self, visitor, o):
        pass


class Program(AST):
    def __init__(self, decls):
        self.decls = decls

    def __str__(self):
        return f"Program([{', '.join(str(d) for d in self.decls)}])"

    def accept(self, visitor, o):
        return visitor.visitProgram(self, o)


class Decl(AST):
    pass


class StructDecl(Decl):
    def __init__(self, name, fields):
        self.name = name  # str
        self.fields = fields  # list[VarDecl]

    def __str__(self):
        fields_str = ', '.join(str(f) for f in self.fields)
        return f"StructDecl(Id({self.name}), [{fields_str}])"

    def accept(self, visitor, o):
        return visitor.visitStructDecl(self, o)


class FuncDecl(Decl):
    def __init__(self, name, params, return_type, body):
        self.name = name  # str
        self.params = params  # list[VarDecl]
        self.return_type = return_type  # Type
        self.body = body  # Block

    def __str__(self):
        params_str = ', '.join(str(p) for p in self.params)
        return f"FuncDecl(Id({self.name}), [{params_str}], {self.return_type}, {self.body})"

    def accept(self, visitor, o):
        return visitor.visitFuncDecl(self, o)


class VarDecl(AST):
    def __init__(self, name, var_type, init=None, is_mut=False):
        self.name = name  # str
        self.var_type = var_type  # Type
        self.init = init  # Expr or None
        self.is_mut = is_mut  # bool

    def __str__(self):
        init_str = str(self.init) if self.init is not None else "None"
        return f"VarDecl(Id({self.name}), {self.var_type}, {init_str}, {self.is_mut})"

    def accept(self, visitor, o):
        return visitor.visitVarDecl(self, o)


class Type(AST):
    pass


class IntType(Type):
    def __str__(self):
        return "IntType"

    def accept(self, visitor, o):
        return visitor.visitIntType(self, o)


class FloatType(Type):
    def __str__(self):
        return "FloatType"

    def accept(self, visitor, o):
        return visitor.visitFloatType(self, o)


class BoolType(Type):
    def __str__(self):
        return "BoolType"

    def accept(self, visitor, o):
        return visitor.visitBoolType(self, o)


class StringType(Type):
    def __str__(self):
        return "StringType"

    def accept(self, visitor, o):
        return visitor.visitStringType(self, o)


class VoidType(Type):
    def __str__(self):
        return "VoidType"

    def accept(self, visitor, o):
        return visitor.visitVoidType(self, o)


class ArrayType(Type):
    def __init__(self, element_type, size):
        self.element_type = element_type  # Type
        self.size = size  # int

    def __str__(self):
        return f"ArrayType({self.element_type}, {self.size})"

    def accept(self, visitor, o):
        return visitor.visitArrayType(self, o)


class StructType(Type):
    def __init__(self, name):
        self.name = name  # str

    def __str__(self):
        return f"StructType(Id({self.name}))"

    def accept(self, visitor, o):
        return visitor.visitStructType(self, o)


class Stmt(AST):
    pass


class Block(Stmt):
    def __init__(self, stmts):
        self.stmts = stmts  # list[Stmt]

    def __str__(self):
        stmts_str = ', '.join(str(s) for s in self.stmts)
        return f"Block([{stmts_str}])"

    def accept(self, visitor, o):
        return visitor.visitBlock(self, o)


class If(Stmt):
    def __init__(self, cond, then_stmt, else_stmt=None):
        self.cond = cond  # Expr
        self.then_stmt = then_stmt  # Stmt
        self.else_stmt = else_stmt  # Stmt or None

    def __str__(self):
        else_str = str(self.else_stmt) if self.else_stmt is not None else "None"
        return f"If({self.cond}, {self.then_stmt}, {else_str})"

    def accept(self, visitor, o):
        return visitor.visitIf(self, o)


class While(Stmt):
    def __init__(self, cond, body):
        self.cond = cond  # Expr
        self.body = body  # Stmt

    def __str__(self):
        return f"While({self.cond}, {self.body})"

    def accept(self, visitor, o):
        return visitor.visitWhile(self, o)


class For(Stmt):
    def __init__(self, var_name, start, end, body):
        self.var_name = var_name  # str
        self.start = start  # Expr
        self.end = end  # Expr
        self.body = body  # Stmt

    def __str__(self):
        return f"For(Id({self.var_name}), {self.start}, {self.end}, {self.body})"

    def accept(self, visitor, o):
        return visitor.visitFor(self, o)


class Switch(Stmt):
    def __init__(self, expr, cases, default_stmt):
        self.expr = expr  # Expr
        self.cases = cases  # list[Case]
        self.default_stmt = default_stmt  # Stmt

    def __str__(self):
        cases_str = ', '.join(str(c) for c in self.cases)
        return f"Switch({self.expr}, [{cases_str}], {self.default_stmt})"

    def accept(self, visitor, o):
        return visitor.visitSwitch(self, o)


class Case(AST):
    def __init__(self, value, body):
        self.value = value  # Expr (Literal)
        self.body = body  # Stmt

    def __str__(self):
        return f"Case({self.value}, {self.body})"

    def accept(self, visitor, o):
        return visitor.visitCase(self, o)


class Break(Stmt):
    def __str__(self):
        return "Break()"

    def accept(self, visitor, o):
        return visitor.visitBreak(self, o)


class Continue(Stmt):
    def __str__(self):
        return "Continue()"

    def accept(self, visitor, o):
        return visitor.visitContinue(self, o)


class Return(Stmt):
    def __init__(self, expr=None):
        self.expr = expr  # Expr or None

    def __str__(self):
        expr_str = str(self.expr) if self.expr is not None else "None"
        return f"Return({expr_str})"

    def accept(self, visitor, o):
        return visitor.visitReturn(self, o)


class ExprStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr  # Expr

    def __str__(self):
        return f"ExprStmt({self.expr})"

    def accept(self, visitor, o):
        return visitor.visitExprStmt(self, o)


class Expr(AST):
    pass


class BinaryOp(Expr):
    def __init__(self, op, left, right):
        self.op = op  # str
        self.left = left  # Expr
        self.right = right  # Expr

    def __str__(self):
        return f"BinaryOp('{self.op}', {self.left}, {self.right})"

    def accept(self, visitor, o):
        return visitor.visitBinaryOp(self, o)


class UnaryOp(Expr):
    def __init__(self, op, body):
        self.op = op  # str
        self.body = body  # Expr

    def __str__(self):
        return f"UnaryOp('{self.op}', {self.body})"

    def accept(self, visitor, o):
        return visitor.visitUnaryOp(self, o)


class CallExpr(Expr):
    def __init__(self, name, args):
        self.name = name  # str
        self.args = args  # list[Expr]

    def __str__(self):
        args_str = ', '.join(str(a) for a in self.args)
        return f"CallExpr(Id({self.name}), [{args_str}])"

    def accept(self, visitor, o):
        return visitor.visitCallExpr(self, o)


class Id(Expr):
    def __init__(self, name):
        self.name = name  # str

    def __str__(self):
        return f"Id({self.name})"

    def accept(self, visitor, o):
        return visitor.visitId(self, o)


class ArrayCell(Expr):
    def __init__(self, arr, idx):
        self.arr = arr  # Expr
        self.idx = idx  # Expr

    def __str__(self):
        return f"ArrayCell({self.arr}, {self.idx})"

    def accept(self, visitor, o):
        return visitor.visitArrayCell(self, o)


class FieldAccess(Expr):
    def __init__(self, obj, field):
        self.obj = obj  # Expr
        self.field = field  # str

    def __str__(self):
        return f"FieldAccess({self.obj}, Id({self.field}))"

    def accept(self, visitor, o):
        return visitor.visitFieldAccess(self, o)


class StructInit(Expr):
    def __init__(self, name, initializers):
        self.name = name  # str
        self.initializers = initializers  # list[FieldInit]

    def __str__(self):
        inits_str = ', '.join(str(i) for i in self.initializers)
        return f"StructInit(Id({self.name}), [{inits_str}])"

    def accept(self, visitor, o):
        return visitor.visitStructInit(self, o)


class FieldInit(AST):
    def __init__(self, name, expr):
        self.name = name  # str
        self.expr = expr  # Expr

    def __str__(self):
        return f"FieldInit(Id({self.name}), {self.expr})"

    def accept(self, visitor, o):
        return visitor.visitFieldInit(self, o)


class Literal(Expr):
    pass


class IntLiteral(Literal):
    def __init__(self, value):
        self.value = value  # int

    def __str__(self):
        return f"IntLiteral({self.value})"

    def accept(self, visitor, o):
        return visitor.visitIntLiteral(self, o)


class FloatLiteral(Literal):
    def __init__(self, value):
        self.value = value  # float

    def __str__(self):
        return f"FloatLiteral({self.value})"

    def accept(self, visitor, o):
        return visitor.visitFloatLiteral(self, o)


class BoolLiteral(Literal):
    def __init__(self, value):
        self.value = value  # bool

    def __str__(self):
        return f"BoolLiteral({self.value})"

    def accept(self, visitor, o):
        return visitor.visitBoolLiteral(self, o)


class StringLiteral(Literal):
    def __init__(self, value):
        self.value = value  # str

    def __str__(self):
        # Format string value to be printed as enclosed in double quotes with appropriate escapes
        escaped = self.value.replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t').replace('"', '\\"')
        return f'StringLiteral("{escaped}")'

    def accept(self, visitor, o):
        return visitor.visitStringLiteral(self, o)


class ArrayLiteral(Literal):
    def __init__(self, elements):
        self.elements = elements  # list[Expr]

    def __str__(self):
        elements_str = ', '.join(str(e) for e in self.elements)
        return f"ArrayLiteral([{elements_str}])"

    def accept(self, visitor, o):
        return visitor.visitArrayLiteral(self, o)


class Assign(Expr):
    def __init__(self, lhs, rhs):
        self.lhs = lhs  # Expr (LValue)
        self.rhs = rhs  # Expr

    def __str__(self):
        return f"Assign({self.lhs}, {self.rhs})"

    def accept(self, visitor, o):
        return visitor.visitAssign(self, o)
