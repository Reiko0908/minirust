from dataclasses import dataclass
from functools import reduce
from typing import Any, Dict, List, Optional, Set, Tuple

from utils.AST import *
from utils.Visitor import BaseVisitor
from checker.StaticError import *

# ===============================================
# Symbol-table Data Structures
# ===============================================
@dataclass(frozen=True)
class VarInfo:
    var_type: Type
    mutable: bool

@dataclass
class FunctionType:
    param_types: List[Type]
    return_type: Type

@dataclass
class Environment:
    scopes: List[Dict[str, VarInfo]]
    param_names: Set[str]
    return_type: Optional[Type]
    loop_depth: int = 0
    switch_depth: int = 0

# ===============================================
# Built-in Function Signatures
# ===============================================
BUILTIN_FUNCS = {
    'print_i32'     : FunctionType([IntType()], VoidType()),
    'println_i32'   : FunctionType([IntType()], VoidType()),
    'print_f32'     : FunctionType([FloatType()], VoidType()),
    'println_f32'   : FunctionType([FloatType()], VoidType()),
    'print_bool'    : FunctionType([BoolType()], VoidType()),
    'println_bool'  : FunctionType([BoolType()], VoidType()),
    'print_string'  : FunctionType([StringType()], VoidType()),
    'println_string': FunctionType([StringType()], VoidType()),
    'println'       : FunctionType([], VoidType())
}

# ===============================================
# Static Checker
# ===============================================
class StaticChecker(BaseVisitor):
    def __init__(self, ast_obj=None):
        self.ast = ast_obj
        self.structs: Dict[str, StructDecl] = {}
        self.struct_fields: Dict[str, Dict[str, Type]] = {}
        self.funcs: Dict[str, FunctionType] = dict(BUILTIN_FUNCS)
        self._struct_colors: Dict[str, int] = {}

    def check(self):
        if self.ast is not None:
            self.visitProgram(self.ast, None)
        return None

    # ===========================================
    # Names / Type Compatibility
    # ===========================================
    @staticmethod
    def _name(id: Any):
        return id.name if isinstance(id, Id) else str(id)

    def _type_eq(self, left: Optional[Type], right: Optional[Type]):
        if left is None or right is None:
            return left is right
        if type(left) is not type(right):
            return False
        if isinstance(left, ArrayType) and isinstance(right, ArrayType):
            return left.size == right.size and self._type_eq(
                left.element_type, right.element_type
            )
        if isinstance(left, StructType) and isinstance(right, StructType):
            return self._name(left.name) == self._name(right.name)
        return True

    def _array_assignable(self, source: ArrayType, target: ArrayType):
        if source.size != target.size:
            return False
        if source.element_type is None:
            return source.size == 0
        if target.element_type is None:
            return False
        if (isinstance(source.element_type, ArrayType)
            and isinstance(target.element_type, ArrayType)
        ):
            return self._array_assignable(source.element_type, target.element_type)
        return self._type_eq(source.element_type, target.element_type)

    def _assignable(self, source: Type, target: Type):
        return self._type_eq(source, target) or (
            isinstance(source, IntType) and isinstance(target, FloatType)
        )

    def _unknown_array_ele(self, typ: Type):
       return isinstance(typ, ArrayType) and (
           typ.element_type is None
           or self._unknown_array_ele(typ.element_type)
       )

    # ===========================================
    # Type Resolution / Global Registration
    # ===========================================
    def _resolve_type(self, typ: Any, ctx: Any, allow_void: bool = False):
        resolved = typ() if isinstance(typ, type) and issubclass(typ, Type) else typ
        if isinstance(resolved, (IntType, FloatType, BoolType, StringType)):
            return resolved
        if isinstance(resolved, VoidType):
            if not allow_void:
                raise TypeMismatchInStatement(ctx)
            return resolved
        if isinstance(resolved, ArrayType):
            if (
                resolved.element_type is None
                or not isinstance(resolved.size, int)
                or isinstance(resolved.size, bool)
                or resolved.size < 0
            ):
                raise TypeMismatchInStatement(ctx)
            return ArrayType(self._resolve_type(resolved.element_type, ctx, False), resolved.size)
        if isinstance(resolved, StructType):
            name = self._name(resolved.name)
            if name not in self.structs:
                raise UndeclaredStruct(name)
            return StructType(Id(name))

        raise TypeMismatchInStatement(ctx)

    def _struct_decl(self, decl: StructDecl):
        struct_name = self._name(decl.name)
        if struct_name in self.structs:
            raise Redeclared("Struct", struct_name)
        self.structs[struct_name] = decl

    def _func_decl(self, decl: FuncDecl):
        func_name = self._name(decl.name)
        if func_name in self.funcs:
            raise Redeclared("Function", func_name)
        reduce(self._validate_param, decl.params, set())
        param_types = list(map(lambda param: self._resolve_type(param.var_type, param, False), decl.params))
        return_type = self._resolve_type(decl.return_type, decl, True)
        self.funcs[func_name] = FunctionType(param_types, return_type)

    def _validate_param(self, seen: Set[str], param: VarDecl):
        param_name = self._name(param.name)
        if param_name in seen:
            raise Redeclared("Parameter", param_name)
        self._resolve_type(param.var_type, param, False)
        seen.add(param_name)
        return seen

    # ===========================================
    # Program / Declarations
    # ===========================================
    def visitProgram(self, ast: Program, o: Any):
        self.structs = {}
        self.struct_fields = {}
        self.funcs = dict(BUILTIN_FUNCS)
        self._struct_colors = {}

        struct_decls = list(filter(lambda decl: isinstance(decl, StructDecl), ast.decls))
        func_decls = list(filter(lambda decl: isinstance(decl, FuncDecl), ast.decls))

        list(map(self._struct_decl, struct_decls))
        list(map(self._func_decl, func_decls))
        list(map(lambda decl: self.visitStructDecl(decl, None), struct_decls))

        self._struct_colors = dict(map(lambda name: (name, 0), self.structs.keys()))
        list(map(lambda name: self._dfs_struct(name)
            if self._struct_colors[name] == 0
            else None, self.structs.keys()
        ))

        main_decl = next(filter(lambda decl: self._name(decl.name) == "main", func_decls), None)
        if main_decl is not None:
            main_type = self.funcs["main"]
            if (
                main_type.param_types
                or not isinstance(main_type.return_type, VoidType)
            ):
                raise TypeMismatchInStatement(main_decl)

        list(map(lambda decl: self.visitFuncDecl(decl, None), func_decls))
        return None

    # ==========================================
    # Struct Recursion Check
    # ==========================================
    def visitStructDecl(self, ast: StructDecl, o: Any):
        _, fields = reduce(
            self._add_struct_field,
            ast.fields,
            (set(), {})
        )
        self.struct_fields[ast.name.name] = fields
        return None

    def _add_struct_field(self, state: Tuple[Set[str], Dict[str, Type]], field: VarDecl):
        seen, fields = state
        field_name = self._name(field.name)
        if field_name in seen:
            raise Redeclared("Member", field_name)
        field_type = self._resolve_type(field.var_type, field, False)
        seen.add(field_name)
        fields[field_name] = field_type
        return (seen, fields)

    def _struct_name(self, typ: Optional[Type]):
        if isinstance(typ, StructType):
            return self._name(typ.name)
        if isinstance(typ, ArrayType):
            return self._struct_name(typ.element_type)
        return None

    def _check_cycle_field(self, field: VarDecl):
        target = self._struct_name(self._resolve_type(field.var_type, field, False))
        if target is None:
            return None
        if self._struct_colors[target] == 1:
            raise TypeMismatchInStatement(field)
        if self._struct_colors[target] == 0:
            self._dfs_struct(target)
        return None

    def _dfs_struct(self, name: str):
        self._struct_colors[name] = 1
        list(map(self._check_cycle_field, self.structs[name].fields))
        self._struct_colors[name] = 2
        return None

    # ==========================================
    # Function / Variable Declarations
    # ==========================================
    def visitFuncDecl(self, ast, o: Any):
        func_sig = self.funcs[self._name(ast.name)]
        param_scope: Dict[str, VarInfo] = dict(map(
            lambda pair: (
                self._name(pair[0].name), VarInfo(pair[1], False)
            ),
            zip(ast.params, func_sig.param_types)
        ))
        env = Environment(
            scopes=[param_scope],
            param_names=set(param_scope.keys()),
            return_type=func_sig.return_type,
        )
        self.visit(ast.body, env)
        return None

    def visitVarDecl(self, ast, o: Any):
        env = o
        name = self._name(ast.name)
        if name in env.scopes[-1] or name in env.param_names:
            raise Redeclared("Variable", name)

        decl_type = self._resolve_type(ast.var_type, ast, False) if ast.var_type is not None else None
        if ast.init is None and not ast.is_mut:
            raise TypeMismatchInStatement(ast)
        init_type = self.visit(ast.init, env) if ast.init is not None else None

        if decl_type is None:
            if init_type is None:
                raise TypeCannotBeInferred(ast)
            if isinstance(init_type, VoidType):
                raise TypeCannotBeInferred(ast)
            if self._unknown_array_ele(init_type):
                raise TypeCannotBeInferred(ast.init)
            var_type = init_type
        else:
            if (
                init_type is not None
                and not self._assignable(init_type, decl_type)
            ):
                raise TypeMismatchInStatement(ast)
            var_type = decl_type
        env.scopes[-1][name] = VarInfo(var_type, ast.is_mut)
        return None

    # ===========================================
    # Scope / LValue Helpers
    # ===========================================
    def _lookup_var(self, name: str, env: Environment):
        result = next(filter(
            lambda value: value is not None,
            map(lambda scope: scope.get(name), reversed(env.scopes))),
            None
        )
        if result is None:
            raise UndeclaredIdentifier(name)
        return result

    def _lvalue_base_name(self, expr: Expr):
        if isinstance(expr, Id):
            return self._name(expr)
        if isinstance(expr, ArrayCell):
            return self._lvalue_base_name(expr.arr)
        if isinstance(expr, FieldAccess):
            return self._lvalue_base_name(expr.obj)
        return None

    # ===========================================
    # Statement / Expression Helpers
    # ===========================================
    def _validate_switch_case(self, state, case: Case):
        ast, env, switch_type, seen_values, default_count = state
        if case.val is None:
            default_count += 1
            if default_count > 1:
                raise TypeMismatchInStatement(ast)
            return (ast, env, switch_type, seen_values, default_count)

        if not isinstance(case.val, (IntLiteral, BoolLiteral)):
            raise TypeMismatchInStatement(ast)
        if not self._type_eq(switch_type, self.visit(case.val, env)):
            raise TypeMismatchInStatement(ast)

        key = (type(case.val), case.val.value)
        if key in seen_values:
            raise TypeMismatchInStatement(ast)
        return (ast, env, switch_type, seen_values | {key}, default_count)

    def _collect_initializer(self, state, initializer: FieldInit):
        ast, initializers = state
        field_name = self._name(initializer.name)
        if field_name in initializers:
            raise TypeMismatchInExpression(ast)
        initializers[field_name] = initializer
        return (ast, initializers)

    def _validate_initializer(self, state, initializer: FieldInit):
        ast, env, decl_fields = state
        field_name = self._name(initializer.name)
        actual_type = self.visit(initializer.expr, env)
        if not self._assignable(actual_type, decl_fields[field_name]):
            raise TypeMismatchInExpression(ast)
        return state

    # ===========================================
    # Statements
    # ===========================================
    def visitBlock(self, ast, o: Any):
        env = o
        block_env = Environment(
            scopes = env.scopes + [{}],
            param_names = env.param_names,
            return_type = env.return_type,
            loop_depth = env.loop_depth,
            switch_depth = env.switch_depth
        )
        list(map(lambda stmt: self.visit(stmt, block_env), ast.stmts))
        return None

    def visitIf(self, ast, o: Any):
        env = o
        cond_type = self.visit(ast.cond, env)
        if not isinstance(cond_type, BoolType):
            raise TypeMismatchInStatement(ast)
        self.visit(ast.then_stmt, env)
        if ast.else_stmt is not None:
            self.visit(ast.else_stmt, env)
        return None

    def visitWhile(self, ast, o: Any):
        env = o
        cond_type = self.visit(ast.cond, env)
        if not isinstance(cond_type, BoolType):
            raise TypeMismatchInStatement(ast)
        loop_env = Environment(
            scopes = env.scopes,
            param_names = env.param_names,
            return_type = env.return_type,
            loop_depth = env.loop_depth + 1,
            switch_depth = env.switch_depth
        )
        self.visit(ast.body, loop_env)
        return None

    def visitFor(self, ast, o: Any):
        env = o
        start_type = self.visit(ast.start, env)
        end_type = self.visit(ast.end, env)
        if not isinstance(start_type, IntType) or not isinstance(end_type, IntType):
            raise TypeMismatchInStatement(ast)

        name = self._name(ast.var_name)
        if name in env.param_names:
            raise Redeclared("Variable", name)
        loop_env = Environment(
            scopes = env.scopes + [{name: VarInfo(IntType(), False)}],
            param_names = env.param_names,
            return_type = env.return_type,
            loop_depth = env.loop_depth + 1,
            switch_depth = env.switch_depth
        )
        if isinstance(ast.body, Block):
            list(map(lambda stmt: self.visit(stmt, loop_env), ast.body.stmts))
        else:
            self.visit(ast.body, loop_env)
        return None

    def visitSwitch(self, ast, o: Any):
        env = o
        switch_type = self.visit(ast.expr, env)
        if not isinstance(switch_type, (IntType, BoolType)) or not ast.cases:
            raise TypeMismatchInStatement(ast)

        switch_env = Environment(
            scopes = env.scopes + [{}],
            param_names = env.param_names,
            return_type = env.return_type,
            loop_depth = env.loop_depth,
            switch_depth = env.switch_depth + 1
        )
        reduce(
            self._validate_switch_case, ast.cases,
            (ast, switch_env, switch_type, set(), 0)
        )
        list(map(lambda case: self.visit(case, switch_env), ast.cases))
        return None

    def visitCase(self, ast, o: Any):
        list(map(lambda stmt: self.visit(stmt, o), ast.body))
        return None

    def visitBreak(self, ast, o: Any):
        env = o
        if env.loop_depth == 0 and env.switch_depth == 0:
            raise MustInLoop(ast)
        return None

    def visitContinue(self, ast, o: Any):
        env = o
        if env.loop_depth == 0:
            raise MustInLoop(ast)
        return None

    def visitReturn(self, ast, o: Any):
        env = o
        if ast.expr is None:
            if not isinstance(env.return_type, VoidType):
                raise TypeMismatchInStatement(ast)
            return  None

        actual_type = self.visit(ast.expr, env)
        if not self._assignable(actual_type, env.return_type):
            raise TypeMismatchInStatement(ast)
        return None

    def visitExprStmt(self, ast, o: Any):
        self.visit(ast.expr, o)
        return None

    # ===========================================
    # Expressions
    # ===========================================
    def visitBinaryOp(self, ast, o: Any) -> Any:
        l_type = self.visit(ast.left, o)
        r_type = self.visit(ast.right, o)
        numeric_types = (IntType, FloatType)

        if ast.op in ("+", "-", "*", "/"):
            if (not isinstance(l_type, numeric_types)
                or not isinstance(r_type, numeric_types)
            ):
                raise TypeMismatchInExpression(ast)
            if isinstance(l_type, FloatType) or isinstance(r_type, FloatType):
                return FloatType()
            return IntType()

        if ast.op == "%":
            if (not isinstance(l_type, IntType)
                or not isinstance(r_type, IntType)
            ):
                raise TypeMismatchInExpression(ast)
            return IntType()

        if ast.op in {"<", "<=", ">", ">=", "==", "!="}:
            if (
                not isinstance(l_type, numeric_types)
                or not isinstance(r_type, numeric_types)
                or not self._type_eq(l_type, r_type)
            ):
                raise TypeMismatchInExpression(ast)
            return BoolType()

        if ast.op in {"&&", "||"}:
            if (not isinstance(l_type, BoolType)
                or not isinstance(r_type, BoolType)
            ):
                raise TypeMismatchInExpression(ast)
            return BoolType()
        raise TypeMismatchInExpression(ast)

    def visitUnaryOp(self, ast, o: Any) -> Any:
        operand_type = self.visit(ast.body, o)
        if ast.op == "-" and isinstance(operand_type, (IntType, FloatType)):
            return operand_type
        if ast.op == "!" and isinstance(operand_type, BoolType):
            return BoolType()
        raise TypeMismatchInExpression(ast)

    def visitCallExpr(self, ast, o: Any) -> Any:
        name = self._name(ast.name)
        func = self.funcs.get(name)
        if func is None:
            raise UndeclaredFunction(name)
        if len(ast.args) != len(func.param_types):
            raise TypeMismatchInExpression(ast)

        arg_types = list(map(lambda arg: self.visit(arg, o), ast.args))
        if not all(map(
            lambda pair: self._assignable(pair[0], pair[1]),
               zip(arg_types, func.param_types)
        )):
            raise TypeMismatchInExpression(ast)
        return func.return_type

    def visitId(self, ast, o: Any) -> Any:
        return self._lookup_var(self._name(ast), o).var_type

    def visitArrayCell(self, ast, o: Any) -> Any:
        arr_type = self.visit(ast.arr, o)
        idx_type = self.visit(ast.idx, o)
        if not isinstance(arr_type, ArrayType) or not isinstance(idx_type, IntType):
            raise TypeMismatchInExpression(ast)
        if arr_type.element_type is None:
            raise TypeMismatchInExpression(ast)
        return arr_type.element_type

    def visitFieldAccess(self, ast, o: Any) -> Any:
        obj_type = self.visit(ast.obj, o)
        if not isinstance(obj_type, StructType):
            raise TypeMismatchInExpression(ast)

        struct_name = self._name(obj_type.name)
        if struct_name not in self.struct_fields:
            raise UndeclaredStruct(struct_name)

        field_name = self._name(ast.field)
        field_type = self.struct_fields[struct_name].get(field_name)
        if field_type is None:
            raise UndeclaredIdentifier(field_name)
        return field_type

    def visitStructInit(self, ast, o: Any) -> Any:
        struct_name = self._name(ast.name)
        if struct_name not in self.structs:
            raise UndeclaredStruct(struct_name)

        _, initializers = reduce(
            self._collect_initializer,
            ast.initializers,
            (ast, {})
        )
        decl_fields = self.struct_fields[struct_name]
        if set(initializers) != set(decl_fields):
            raise TypeMismatchInExpression(ast)

        reduce(
            self._validate_initializer,
            initializers.values(),
            (ast, o, decl_fields)
        )
        return StructType(Id(struct_name))

    def visitFieldInit(self, ast, o: Any) -> Any:
        return self._name(ast.name), self.visit(ast.expr, o)

    def visitArrayLiteral(self, ast, o: Any) -> Any:
        if not ast.elements:
            return ArrayType(None, 0)

        element_types = list(map(lambda element: self.visit(element, o), ast.elements))
        if any(map(lambda ele_type: isinstance(ele_type, VoidType), element_types)):
            raise TypeMismatchInExpression(ast)

        first_type = element_types[0]
        if not all(map(lambda ele_type: self._type_eq(ele_type, first_type), element_types)):
            raise TypeMismatchInExpression(ast)
        return ArrayType(first_type, len(element_types))

    def visitAssign(self, ast, o: Any) -> Any:
        lvalue_name = self._lvalue_base_name(ast.lhs)
        if lvalue_name is None:
            raise TypeMismatchInExpression(ast)

        l_type = self.visit(ast.lhs, o)
        lvalue_info = self._lookup_var(lvalue_name, o)
        if not lvalue_info.mutable:
            raise CannotAssignToConstant(ast.lhs)

        r_type = self.visit(ast.rhs, o)
        if not self._assignable(r_type, l_type):
            raise TypeMismatchInExpression(ast)
        return VoidType()

    # ===========================================
    # Literals / Type Visitors
    # ===========================================
    def visitIntLiteral(self, ast, o: Any) -> Any:
        return IntType()

    def visitFloatLiteral(self, ast, o: Any) -> Any:
        return FloatType()

    def visitBoolLiteral(self, ast, o: Any) -> Any:
        return BoolType()

    def visitStringLiteral(self, ast, o: Any) -> Any:
        return StringType()

    def visitIntType(self, ast, o: Any) -> Any:
        return IntType()

    def visitFloatType(self, ast, o: Any) -> Any:
        return FloatType()

    def visitBoolType(self, ast, o: Any) -> Any:
        return BoolType()

    def visitStringType(self, ast, o: Any) -> Any:
        return StringType()

    def visitVoidType(self, ast, o: Any) -> Any:
        return VoidType()

    def visitArrayType(self, ast, o: Any) -> Any:
        return self._resolve_type(ast, ast, False)

    def visitStructType(self, ast, o: Any) -> Any:
        return self._resolve_type(ast, ast, False)
