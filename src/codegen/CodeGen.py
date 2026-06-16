"""
Code Generator skeleton for MiniRust.
"""

from typing import Any
from utils.AST import *
from utils.Visitor import BaseVisitor
from codegen.Emitter import Emitter
from codegen.Frame import Frame
from codegen.Io import IO_SYMBOL_LIST
from codegen.Utils import Symbol, FunctionType, CName, SubBody, Access, Index

class StringArrayType:
    """Marker type for JVM main(String[] args)."""
    pass

class CodeGenerator(BaseVisitor):
    def __init__(self):
        self.emit = None
        self.class_name = "MiniRustProgram"
        self.functions = {}

    def visitProgram(self, node: Program, o: Any = None):
        self.emit = Emitter(f"{self.class_name}.j")
        self.emit.print_out(self.emit.emit_prolog(self.class_name))

        # Register standard library functions (using map instead of a for loop)
        list(map(lambda sym: self.functions.update({sym.name: sym}), IO_SYMBOL_LIST))

        # Find the single main function declaration
        main_decl = list(filter(lambda d: isinstance(d, FuncDecl) and d.name == "main", node.decls))[0]
        self.functions["main"] = Symbol("main", FunctionType([StringArrayType()], VoidType()), CName(self.class_name))

        self.visit(main_decl, None)
        self.emit.emit_epilog()

    def visitFuncDecl(self, node: FuncDecl, o: Any = None):
        frame = Frame(node.name, VoidType())
        frame.enter_scope(True)
        mtype = FunctionType([StringArrayType()], VoidType())

        self.emit.print_out(self.emit.emit_method(node.name, mtype, True))

        start_label = frame.get_start_label()
        end_label = frame.get_end_label()
        self.emit.print_out(self.emit.emit_label(start_label, frame))

        args_idx = frame.get_new_index()
        self.emit.print_out(
            self.emit.emit_var(
                args_idx, "args", StringArrayType(), start_label, end_label
            )
        )

        # Visit the single statement in the main block directly without a loop
        single_stmt = node.body.stmts[0]
        self.visit(single_stmt, SubBody(frame, []))

        self.emit.print_out(self.emit.emit_return(VoidType(), frame))
        self.emit.print_out(self.emit.emit_label(end_label, frame))
        
        frame.exit_scope()
        self.emit.print_out(self.emit.emit_end_method(frame))

    def visitExprStmt(self, node: ExprStmt, o: SubBody = None):
        code, _ = self.visit(node.expr, Access(o.frame, o.sym))
        self.emit.print_out(code)
        return o

    def visitCallExpr(self, node: CallExpr, o: Access = None):
        frame = o.frame
        fn_sym = self.functions[node.name]
        # Evaluate the single argument directly
        arg_code, _ = self.visit(node.args[0], o)
        code = arg_code + self.emit.emit_invoke_static(f"{fn_sym.value.value}/{node.name}", fn_sym.type, frame)
        return code, fn_sym.type.return_type

    def visitIntLiteral(self, node: IntLiteral, o: Access = None):
        return self.emit.emit_push_iconst(node.value, o.frame), IntType()
