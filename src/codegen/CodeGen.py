"""
Code Generator skeleton for MiniRust.
"""
from dataclasses import dataclass
from functools import reduce
from typing import Any

from codegen.Emitter import CodeGenStructType, Emitter
from codegen.Frame import Frame
from codegen.Io import IO_SYMBOL_LIST
from codegen.Utils import (
    Access,
    CName,
    FunctionType,
    Index,
    SubBody,
    Symbol,
)
from utils.AST import *
from utils.Visitor import BaseVisitor

JASMIN_RESERVED_NAMES = frozenset((
    "class", "super", "source", "field", "method", "end",
    "limit", "var", "line", "throws", "catch", "inner",
    "outer", "new", "return", "goto", "invokevirtual",
    "invokestatic", "invokespecial", "getfield", "putfield"
))

class StringArrayType:
    """Marker type for JVM main(String[] args)."""

@dataclass(slots=True)
class StructInfo:
    name: str
    jvm_name: str
    fields: dict[str, Type]

    def field_type(self, field_name: str) -> Type:
        return self.fields[field_name]

class CodeGenerator(BaseVisitor):
    """Generate executable Jasmin files for a statically valid MiniRust AST."""

    def __init__(self):
        self.class_name = "MiniRustProgram"
        self.emit: Emitter
        self.functions: dict[str, Symbol] = {}
        self.structs: dict[str, StructInfo] = {}
        self.global_symbols: list[Symbol] = []
        self._var_directives: list[str] = []
        self._method_locals: list[Symbol] = []
        self.expected_type: Type | None = None
        self.break_target: list[int] = []

    # -------------------------------------------
    # Name / JVM Types
    # -------------------------------------------
    @staticmethod
    def _name(id: Any) -> str:
        return id.name if isinstance(id, Id) else str(id)

    @staticmethod
    def _jvm_name(name: str, prefix: str) -> str:
        return (
            f"{prefix}{name}"
            if name.lower() in JASMIN_RESERVED_NAMES else name
        )

    def _jvm_type(self, typ: Type) -> Type:
        if isinstance(typ, StructType):
            source_name = self._name(typ.name)
            return CodeGenStructType(self.structs[source_name].jvm_name)
        if isinstance(typ, ArrayType):
            return ArrayType(self._jvm_type(typ.element_type), typ.size)
        if isinstance(typ, FunctionType):
            return FunctionType(
                list(map(self._jvm_type, typ.param_types)),
                self._jvm_type(typ.return_type)
            )
        return typ

    def _coerce(self, code: str, source: Type, target: Type, frame: Frame) -> tuple[str, Type]:
        if isinstance(source, IntType) and isinstance(target, FloatType):
            return code + self.emit.emit_i2f(frame), target
        return code, source

    # -------------------------------------------
    # Type / Global Registration
    # -------------------------------------------
    def _register_struct(self, decl: StructDecl):
        struct_name = self._name(decl.name)
        fields = dict(map(
            lambda f: (self._name(f.name), f.var_type),
            decl.fields
        ))
        self.structs[struct_name] = StructInfo(struct_name, self._jvm_name(struct_name, "_MR_"), fields)

    def _register_func(self, decl: FuncDecl):
        func_name = self._name(decl.name)
        func = Symbol(
            func_name,
            FunctionType(
                list(map(lambda p: p.var_type, decl.params)), decl.return_type
            ),
            CName(self.class_name)
        )
        self.functions[func_name] = func
        self.global_symbols.insert(0, func)

    # -------------------------------------------
    # Program / Struct Declarations
    # -------------------------------------------
    def visitProgram(self, ast: Program, o: Any = None) -> Any:
        self.functions = dict(
            map(lambda f: (f.name, f), IO_SYMBOL_LIST)
        )
        self.structs = {}
        self.global_symbols = list(IO_SYMBOL_LIST)

        struct_decl = list(filter(lambda d: isinstance(d, StructDecl), ast.decls))
        func_decl = list(filter(lambda d: isinstance(d, FuncDecl), ast.decls))
        list(map(self._register_struct, struct_decl))
        list(map(self._register_func, func_decl))
        list(map(lambda d: self.visitStructDecl(d, None), struct_decl))

        self.emit = Emitter(f"{self.class_name}.j")
        self.emit.print_out(self.emit.emit_prolog(self.class_name))
        list(map(lambda d: self.visitFuncDecl(d, None), func_decl))

        if "main" in self.functions:
            self._emit_jvm_main()
        self.emit.emit_epilog()
        return None

    def visitStructDecl(self, ast: StructDecl, o: Any = None) -> Any:
        name = self._name(ast.name)
        info = self.structs[name]
        emitter = Emitter(f"{name}.j")
        emitter.print_out(emitter.emit_prolog(info.jvm_name))
        list(map(
            lambda f: emitter.print_out(
                emitter.emit_field(
                    self._jvm_name(f[0], "_mr_field_"), self._jvm_type(f[1])
                )
            ),
            info.fields.items(),
        ))
        constructor_frame = Frame("<init>", VoidType())
        constructor_frame.get_new_index()
        constructor_code = emitter.emit_method("<init>", FunctionType([], VoidType()), False)
        constructor_code += emitter.emit_read_var("this", StructType(Id(name)), 0, constructor_frame)
        constructor_code += emitter.emit_invoke_special("java/lang/Object/<init>",FunctionType([], VoidType()),constructor_frame)
        constructor_code += emitter.emit_return(VoidType(),constructor_frame,)
        constructor_code += emitter.emit_end_method(constructor_frame)
        emitter.print_out(constructor_code)
        emitter.emit_epilog()
        return None

    def _emit_jvm_main(self):
        target = self.functions["main"]
        desc = FunctionType([ArrayType(StringType(), 0)], VoidType())
        frame = Frame("main", VoidType())
        frame.get_new_index()
        code = self.emit.emit_method("main", desc, True)
        owner = target.value.value
        code += self.emit.emit_invoke_static(
            f"{owner}/{self._jvm_name(target.name, '_mr_fn_')}",
            self._jvm_type(target.type), frame,
        )
        code += self.emit.emit_return(VoidType(), frame)
        code += self.emit.emit_end_method(frame)
        self.emit.print_out(code)

    # -------------------------------------------
    # Function / Variable Declarations
    # -------------------------------------------
    def _alloc_param(self, state, item):
        frame, symbols, start_label, end_label = state
        param, param_type = item
        symbol = Symbol(self._name(param.name), param_type, Index(frame.get_new_index()))
        self._var_directives.append(
            self.emit.emit_var(
                symbol.value.value, f"_mr_var_{symbol.name}",
                self._jvm_type(symbol.type),start_label, end_label,
            )
        )
        return frame, [symbol] + symbols, start_label, end_label

    def _default_init(self, symbol: Symbol, frame: Frame) -> str:
        typ = symbol.type
        idx = symbol.value.value
        if isinstance(typ, (IntType, BoolType)):
            code = self.emit.emit_push_iconst(0, frame)
        elif isinstance(typ, FloatType):
            code = self.emit.emit_push_fconst(0.0, frame)
        else:
            code = self.emit.emit_push_null(frame)
        return code + self.emit.emit_write_var(symbol.name, typ, idx, frame)

    def _can_fall_through(self, stmt: Any) -> bool:
        if isinstance(stmt, (Return, Break, Continue)):
            return False
        if isinstance(stmt, Block):
            return reduce(lambda acc, s: acc and self._can_fall_through(s), stmt.stmts, True)
        if isinstance(stmt, If) and stmt.else_stmt is not None:
            return (
                self._can_fall_through(stmt.then_stmt)
                or self._can_fall_through(stmt.else_stmt)
            )
        return True

    def visitFuncDecl(self, ast: FuncDecl, o: Any = None) -> Any:
        name = self._name(ast.name)
        func = self.functions[name]
        frame = Frame(name, func.type.return_type)
        frame.enter_scope(True)
        method_start = frame.get_start_label()
        method_end = frame.get_end_label()
        self._var_directives = []
        self._method_locals = []
        param_state = reduce(self._alloc_param,
            zip(ast.params, func.type.param_types),
            (frame, list(self.global_symbols), method_start, method_end)
        )
        symbols = param_state[1]
        body_code = self.visit(ast.body, self._subbody(frame, symbols))
        init_code = reduce(
            lambda code, symbol: code + self._default_init(symbol, frame), self._method_locals, ""
        )
        fallthrough_code = (
            self.emit.emit_return(VoidType(), frame)
            if self._can_fall_through(ast.body) and isinstance(func.type.return_type, VoidType) else ""
        )
        frame.check_op_stack()

        code = self.emit.emit_method(self._jvm_name(name, "_mr_fn_"), self._jvm_type(func.type), True)
        code += "".join(self._var_directives)
        code += self.emit.emit_label(method_start, None)
        code += init_code
        code += body_code
        code += self.emit.emit_label(method_end, None)
        code += fallthrough_code
        code += self.emit.emit_end_method(frame)
        frame.exit_scope()
        frame.set_curr_index(frame.get_max_index())
        self.emit.print_out(code)
        return None

    def visitVarDecl(self, ast: VarDecl, o: SubBody) -> Any:
        decl_type = ast.var_type
        init_code = ""
        init_type = None
        if ast.init is not None:
            init_code, init_type = self._expr(ast.init, o, decl_type)
        var_type = decl_type or init_type or IntType()
        name = self._name(ast.name)
        symbol = Symbol(name, var_type, Index(o.frame.get_new_index()))
        o.sym.insert(0, symbol)
        self._method_locals.append(symbol)
        var_start = o.frame.get_new_label()
        scope_end = o.frame.get_end_label()
        self._var_directives.append(
            self.emit.emit_var(
                symbol.value.value, f"_mr_var_{symbol.name}",
                self._jvm_type(symbol.type), var_start, scope_end,
            )
        )
        code = self.emit.emit_label(var_start, None)
        if ast.init is not None:
            code += init_code
            code += self.emit.emit_write_var(symbol.name, symbol.type, symbol.value.value, o.frame)
        else:
            code += self._default_init(symbol, o.frame)
        return code

    # -------------------------------------------
    # Scope / Expression Context
    # -------------------------------------------
    @staticmethod
    def _lookup(symbols: list[Symbol], name: str) -> Symbol:
        symbol = next(filter(lambda s: s.name == name, symbols), None)
        if symbol is None:
            raise KeyError(name)
        return symbol

    def _expr(self, node: Expr, context: SubBody | Access, expected_type: Type | None = None, is_left: bool = False) -> tuple[str, Type]:
        access = Access(context.frame, context.sym, is_left)
        previous_type = self.expected_type
        self.expected_type = expected_type
        code, actual_type = self.visit(node, access)
        self.expected_type = previous_type

        if expected_type is None:
            return code, actual_type
        return self._coerce(code, actual_type, expected_type, context.frame)

    @staticmethod
    def _subbody(frame: Frame, symbols: list[Symbol]) -> SubBody:
        return SubBody(frame, symbols)

    # -------------------------------------------
    # Statement / Expression Helpers
    # -------------------------------------------
    def _switch_test(self, item, context: SubBody, control_symbol: Symbol, control_type: Type) -> str:
        case, label = item
        if case.val is None:
            return ""
        case_code, _ = self._expr(case.val, context, control_type)
        code = self.emit.emit_read_var(
            control_symbol.name, control_type,
            control_symbol.value.value, context.frame
        ) + case_code
        return code + self.emit.emit_if_icmpeq(label, context.frame)

    def _emit_field_init(self, code: str, init: FieldInit, context: Access, info: StructInfo) -> str:
        field_name = self._name(init.name)
        field_type = info.field_type(field_name)
        dup_code = self.emit.emit_dup(context.frame)
        value_code, _ = self._expr(init.expr, context, field_type)
        field_code = self.emit.emit_put_field(
            f"{info.jvm_name}/{self._jvm_name(field_name, '_mr_field_')}",
            self._jvm_type(field_type), context.frame
        )
        return code + dup_code + value_code + field_code

    def emit_array_element(self, state, item):
        code, element_type, context, cached_first = state
        idx, element = item
        dup_code = self.emit.emit_dup(context.frame)
        idx_code = self.emit.emit_push_iconst(idx, context.frame)
        if idx == 0 and cached_first is not None:
            element_code, _ = cached_first
            context.frame.push()
        else:
            element_code, _ = self._expr(element, context, element_type)
        element_code += self.emit.emit_array_store(element_type, context.frame)
        return code + dup_code + idx_code + element_code, element_type, context, cached_first

    # -------------------------------------------
    # Statements
    # ------------------------------------------
    def visitBlock(self, ast: Block, o: SubBody) -> Any:
        o.frame.enter_scope(False)
        start_label = o.frame.get_start_label()
        end_label = o.frame.get_end_label()
        body_context = self._subbody(o.frame, list(o.sym))
        code = self.emit.emit_label(start_label, None)
        code += reduce(
            lambda result, stmt: result + self.visit(stmt, body_context), ast.stmts, ""
        )
        code += self.emit.emit_label(end_label, None)
        o.frame.exit_scope()
        o.frame.set_curr_index(o.frame.get_max_index())
        return code

    def visitIf(self, ast: If, o: SubBody) -> Any:
        cond_code, _ = self._expr(ast.cond, o)
        false_label = o.frame.get_new_label()
        end_label = o.frame.get_new_label()
        code = cond_code + self.emit.emit_if_false(false_label, o.frame)
        code += self.visit(ast.then_stmt, self._subbody(o.frame, list(o.sym)))

        if ast.else_stmt is not None:
            if self._can_fall_through(ast.then_stmt):
                code += self.emit.emit_goto(end_label, o.frame)
            code += self.emit.emit_label(false_label, None)
            code += self.visit(ast.else_stmt, self._subbody(o.frame, list(o.sym)))
            code += self.emit.emit_label(end_label, None)
        else:
            code += self.emit.emit_label(false_label, None)
        return code

    def visitWhile(self, ast: While, o: SubBody) -> Any:
        o.frame.enter_loop()
        cond_label = o.frame.get_continue_label()
        exit_label = o.frame.get_break_label()
        self.break_target.append(exit_label)
        body_code = self.visit(ast.body, self._subbody(o.frame, list(o.sym)))
        self.break_target.pop()
        cond_code, _ = self._expr(ast.cond, o)

        code = self.emit.emit_label(cond_label, None)
        code += cond_code
        code += self.emit.emit_if_false(exit_label, o.frame)
        code += body_code
        code += self.emit.emit_goto(cond_label, o.frame)
        code += self.emit.emit_label(exit_label, None)
        o.frame.exit_loop()
        return code

    def visitFor(self, ast: For, o: SubBody) -> Any:
        o.frame.enter_scope(False)
        scope_start = o.frame.get_start_label()
        scope_end = o.frame.get_end_label()
        loop_var = Symbol(self._name(ast.var_name), IntType(), Index(o.frame.get_new_index()))
        self._method_locals.append(loop_var)
        var_start = o.frame.get_new_label()
        cond_label = o.frame.get_new_label()

        start_code, _ = self._expr(ast.start, o, IntType())
        loop_idx = loop_var.value.value
        start_code += self.emit.emit_write_var(loop_var.name, loop_var.type, loop_idx, o.frame)

        o.frame.enter_loop()
        cont_label = o.frame.get_continue_label()
        exit_label = o.frame.get_break_label()
        loop_symbols = [loop_var] + list(o.sym)
        loop_context = self._subbody(o.frame, loop_symbols)
        compare_code = self.emit.emit_read_var(
            loop_var.name, loop_var.type, loop_idx, o.frame
        )
        end_code, _ = self._expr(ast.end, loop_context, IntType())
        compare_code += end_code
        self.break_target.append(exit_label)
        body_code = self.visit(ast.body, loop_context)
        self.break_target.pop()
        self._var_directives.append(
            self.emit.emit_var(
                loop_idx, f"_mr_var_{loop_var.name}",
                self._jvm_type(loop_var.type), var_start, scope_end
            )
        )

        code = self.emit.emit_label(scope_start, None)
        code += self.emit.emit_label(var_start, None)
        code += start_code
        code += self.emit.emit_label(cond_label, None)
        code += compare_code
        code += self.emit.emit_if_icmpge(exit_label, o.frame)
        code += body_code
        code += self.emit.emit_label(cont_label, None)
        code += self.emit.emit_iinc(loop_idx, 1, o.frame)
        code += self.emit.emit_goto(cond_label, o.frame)
        code += self.emit.emit_label(exit_label, None)
        code += self.emit.emit_label(scope_end, None)
        o.frame.exit_loop()
        o.frame.exit_scope()
        o.frame.set_curr_index(o.frame.get_max_index())
        return code

    def visitSwitch(self, ast: Switch, o:SubBody) -> Any:
        control_code, control_type = self._expr(ast.expr, o)
        o.frame.enter_scope(False)
        scope_start = o.frame.get_start_label()
        exit_label = o.frame.get_end_label()
        control_symbol = Symbol("", control_type, Index(o.frame.get_new_index()))
        self._method_locals.append(control_symbol)
        control_code += self.emit.emit_write_var(
            control_symbol.name, control_symbol.type,
            control_symbol.value.value, o.frame
        )
        case_labels = list(map(
            lambda c: o.frame.get_new_label(), ast.cases
        ))
        labelled_cases = list(zip(ast.cases, case_labels))
        default_label = reduce(
            lambda result, case: case[1]
            if case[0].val is None else result, labelled_cases, exit_label
        )
        switch_context = self._subbody(o.frame, list(o.sym))
        switch_chain = control_code
        switch_chain += reduce(
            lambda result, case: result + self._switch_test(case, switch_context, control_symbol, control_type),
            labelled_cases, ""
        )
        switch_chain += self.emit.emit_goto(default_label, None)

        self.break_target.append(exit_label)
        body_code = reduce(
            lambda result, case: result + self.emit.emit_label(case[1], None) + self.visit(case[0], switch_context),
            labelled_cases, ""
        )
        self.break_target.pop()
        code = self.emit.emit_label(scope_start, None)
        code += switch_chain
        code += body_code
        code += self.emit.emit_label(exit_label, None)
        o.frame.exit_scope()
        o.frame.set_curr_index(o.frame.get_max_index())
        return code

    def visitCase(self, ast: Case, o: SubBody) -> Any:
        return reduce(
            lambda result, stmt: result + self.visit(stmt, o),
            ast.body, ""
        )

    def visitBreak(self, ast: Break, o: SubBody) -> Any:
        return self.emit.emit_goto(self.break_target[-1], None)

    def visitContinue(self, ast: Continue, o: SubBody) -> Any:
        return self.emit.emit_goto(o.frame.get_continue_label(), None)

    def visitReturn(self, ast: Return, o: SubBody) -> Any:
        if ast.expr is None:
            return self.emit.emit_return(VoidType(), o.frame)

        code, actual_type = self._expr(ast.expr, o, o.frame.return_type)
        if isinstance(o.frame.return_type, VoidType):
            if not isinstance(actual_type, VoidType):
                code += self.emit.emit_pop(o.frame)
            return code + self.emit.emit_return(VoidType(), o.frame)
        return code + self.emit.emit_return(o.frame.return_type, o.frame)

    def visitExprStmt(self, ast: ExprStmt, o: SubBody) -> Any:
        code, result_type = self._expr(ast.expr,o)
        if not isinstance(result_type, VoidType):
            code += self.emit.emit_pop(o.frame)
        return code

    # -------------------------------------------
    # Expressions
    # -------------------------------------------
    def visitBinaryOp(self, ast: BinaryOp, o: Access) -> Any:
        frame = o.frame
        op = ast.op

        if op in ("&&", "||"):
            left_code, _ = self._expr(ast.left, o)
            branch_label = frame.get_new_label()
            end_label = frame.get_new_label()
            is_and_op = (op == "&&")
            emit_branch = (
                self.emit.emit_if_false
                if is_and_op else self.emit.emit_if_true
            )
            fallthrough_val, branch_val = (1,0) if is_and_op else (0,1)
            left_branch = emit_branch(branch_label, frame)
            right_code, _ = self._expr(ast.right, o)
            right_branch = emit_branch(branch_label, frame)
            branch_stack = frame.get_stack_size()
            code = left_code + left_branch
            code += right_code + right_branch
            code += self.emit.emit_push_iconst(fallthrough_val, frame)
            code += self.emit.emit_goto(end_label, None)
            self.emit._restore_stack(frame, branch_stack)
            code += self.emit.emit_label(branch_label, None)
            code += self.emit.emit_push_iconst(branch_val, frame)
            code += self.emit.emit_label(end_label, None)
            return code, BoolType()

        left_code, left_type = self._expr(ast.left, o)
        right_code, right_type = self._expr(ast.right, o)
        has_float = isinstance(left_type, FloatType) or isinstance(right_type, FloatType)
        if op in ("+", "-", "*", "/"):
            result_type = FloatType() if has_float else IntType()
            left_code, _ = self._coerce(left_code, left_type, result_type, frame)
            right_code, _ = self._coerce(right_code, right_type, result_type, frame)
            emit_op = (self.emit.emit_add_op
                if op in ("+", "-") else self.emit.emit_mul_op
            )
            code = left_code + right_code + emit_op(op, result_type, frame)
            return code, result_type
        if op == "%":
            return left_code + right_code + self.emit.emit_mod(frame), IntType()
        if op in ("==", "!=", "<", "<=", ">", ">="):
            compare_type = FloatType() if has_float else left_type
            left_code, _ = self._coerce(left_code, left_type, compare_type, frame)
            right_code, _ = self._coerce(right_code, right_type, compare_type, frame)
            code = left_code + right_code + self.emit.emit_re_op(op, compare_type, frame)
            return code, BoolType()
        raise ValueError(f"Unsupported binary operator: {op}")

    def visitUnaryOp(self, ast: UnaryOp, o: Access) -> Any:
        code, operand_type = self._expr(ast.body, o)
        if ast.op == "-":
            ins = self.emit.emit_neg_op(operand_type, o.frame)
            return code + ins, operand_type
        if ast.op == "!":
            ins = self.emit.emit_push_iconst(0, o.frame)
            ins += self.emit.emit_re_op("==", BoolType(), o.frame)
            return code + ins, BoolType()
        raise ValueError(f"Unsupported unary operator: {ast.op}")

    def visitCallExpr(self, ast: CallExpr, o: Access) -> Any:
        name = self._name(ast.name)
        func = self.functions[name]
        code = reduce(
            lambda result, arg: result + self._expr(arg[0], o, arg[1])[0],
            zip(ast.args, func.type.param_types), ""
        )
        owner = func.value.value
        code += self.emit.emit_invoke_static(
            f"{owner}/{self._jvm_name(func.name, '_mr_fn_')}",
            self._jvm_type(func.type), o.frame
        )
        return code, func.type.return_type

    def visitId(self, ast: Id, o: Access) -> Any:
        sym = self._lookup(o.sym, self._name(ast))
        idx = sym.value.value
        code = (
            self.emit.emit_write_var(sym.name, sym.type,idx,o.frame)
            if o.is_left
            else self.emit.emit_read_var(sym.name,sym.type, idx, o.frame)
        )
        return code, sym.type

    def visitArrayCell(self, ast: ArrayCell, o: Access) -> Any:
        array_code, array_type = self._expr(ast.arr, o)
        idx_code, _ = self._expr(ast.idx, o, IntType())
        element_type = array_type.element_type
        return (array_code + idx_code
            + self.emit.emit_array_load(element_type, o.frame), element_type,
        )

    def visitFieldAccess(self, ast: FieldAccess, o: Access) -> Any:
        obj_code, obj_type = self._expr(ast.obj, o)
        struct_name = self._name(obj_type.name)
        jvm_struct_name = self.structs[struct_name].jvm_name
        field_name = self._name(ast.field)
        field_type = self.structs[struct_name].fields[field_name]
        code = obj_code
        code += self.emit.emit_get_field(
            f"{jvm_struct_name}/{self._jvm_name(field_name, '_mr_field_')}",
            self._jvm_type(field_type), o.frame,
        )
        return code, field_type

    def visitStructInit(self, ast: StructInit, o: Access) -> Any:
        name = self._name(ast.name)
        info = self.structs[name]
        code = self.emit.emit_new_instance(info.jvm_name, o.frame)
        code = reduce(
            lambda result, init: self._emit_field_init(result, init, o, info),
            ast.initializers, code
        )
        return code, StructType(Id(name))

    def visitFieldInit(self, ast: FieldInit, o: Access) -> Any:
        return self._expr(ast.expr, o, self.expected_type)

    def visitArrayLiteral(self, ast: ArrayLiteral, o: Access) -> Any:
        expected = (
            self.expected_type
            if isinstance(self.expected_type, ArrayType) else None
        )
        element_type = expected.element_type if expected is not None else None
        cached_first = None
        if element_type is None and ast.elements:
            baseline = o.frame.get_stack_size()
            self.emit._restore_stack(o.frame, baseline + 3)
            first_code, element_type = self._expr(ast.elements[0], o)
            cached_first = first_code, element_type
            self.emit._restore_stack(o.frame, baseline)
        if element_type is None:
            element_type = IntType()

        code = self.emit.emit_push_iconst(len(ast.elements), o.frame)
        code += self.emit.emit_new_array(self._jvm_type(element_type), o.frame)
        array_state = reduce(
            self.emit_array_element, enumerate(ast.elements),
            (code, element_type, o, cached_first),
        )
        code = array_state[0]
        return code, ArrayType(element_type, len(ast.elements))

    def visitAssign(self, ast: Assign, o: Access) -> Any:
        if isinstance(ast.lhs, Id):
            sym = self._lookup(o.sym, self._name(ast.lhs))
            value_code, _ = self._expr(ast.rhs, o, sym.type)
            value_code += self.emit.emit_dup(o.frame)
            store_code, _ = self._expr(ast.lhs, o, sym.type, is_left=True)
            return value_code + store_code, sym.type
        if isinstance(ast.lhs, ArrayCell):
            array_code, array_type = self._expr(ast.lhs.arr, o)
            idx_code, _ = self._expr(ast.lhs.idx, o, IntType())
            target_type = array_type.element_type
            value_code, _ = self._expr(ast.rhs, o, array_type.element_type)
            code = array_code + idx_code + value_code
            code += self.emit.emit_dup_x2(o.frame)
            code += self.emit.emit_array_store(target_type, o.frame)
            return code, target_type
        if isinstance(ast.lhs, FieldAccess):
            obj_code, obj_type = self._expr(ast.lhs.obj, o)
            struct_name = self._name(obj_type.name)
            jvm_struct_name = self.structs[struct_name].jvm_name
            field_name = self._name(ast.lhs.field)
            target_type = self.structs[struct_name].fields[field_name]
            value_code, _ = self._expr(ast.rhs, o, target_type)
            code = obj_code + value_code
            code += self.emit.emit_dup_x1(o.frame)
            code += self.emit.emit_put_field(
                f"{jvm_struct_name}/{self._jvm_name(field_name, '_mr_field_')}",
                self._jvm_type(target_type), o.frame,
            )
            return code, target_type
        raise ValueError(f"Unsupported assignment target: {ast.lhs}")

    # -------------------------------------------
    # Literals / Types Visitors
    # -------------------------------------------
    def visitIntLiteral(self, ast: IntLiteral, o: Access) -> Any:
        return self.emit.emit_push_iconst(ast.value, o.frame), IntType()

    def visitFloatLiteral(self, ast: FloatLiteral, o: Access) -> Any:
        return self.emit.emit_push_fconst(ast.value, o.frame), FloatType()

    def visitBoolLiteral(self, ast: BoolLiteral, o: Access) -> Any:
        return self.emit.emit_push_iconst(1 if ast.value else 0, o.frame), BoolType()

    def visitStringLiteral(self, ast: StringLiteral, o: Access) -> Any:
        return self.emit.emit_push_const(ast.value, StringType(), o.frame), StringType()

    def visitIntType(self, ast: IntType, o: Any) -> Any:
        return IntType()

    def visitFloatType(self, ast: FloatType, o: Any) -> Any:
        return FloatType()

    def visitBoolType(self, ast: BoolType, o: Any) -> Any:
        return BoolType()

    def visitStringType(self, ast: StringType, o: Any) -> Any:
        return StringType()

    def visitVoidType(self, ast: VoidType, o: Any) -> Any:
        return VoidType()

    def visitArrayType(self, ast: ArrayType, o: Any) -> Any:
        return ast

    def visitStructType(self, ast: StructType, o: Any) -> Any:
        return ast
