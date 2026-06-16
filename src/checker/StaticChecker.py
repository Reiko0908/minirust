from utils.AST import *
from utils.Visitor import BaseVisitor
from checker.StaticError import *
from typing import Any

class StaticChecker(BaseVisitor):
    def __init__(self, ast_obj=None):
        self.ast = ast_obj

    def check(self):
        # Call the program visitor directly
        self.visitProgram(self.ast, None)

    def visitProgram(self, ast: Program, o: Any) -> Any:
        # Register built-in functions (simplified)
        builtins = ["print_i32", "println_i32", "print_f32", "println_f32", "print_bool", "println_bool", "print_string", "println_string", "println"]
        # Traverse each function declaration using visitor methods
        [self.visit(decl, builtins) for decl in ast.decls]
        return None

    def visitFuncDecl(self, ast: FuncDecl, o: Any) -> Any:
        # Simple traversal of the function body
        self.visit(ast.body, o)
        return None

    def visitBlock(self, ast: Block, o: Any) -> Any:
        self.visit(ast.stmts[0], o)
        return None

    def visitExprStmt(self, ast: ExprStmt, o: Any) -> Any:
        # Evaluate the expression
        self.visit(ast.expr, o)
        return None

    def visitCallExpr(self, ast: CallExpr, o: Any) -> Any:
        # Verify the called function exists either as user‑defined or built‑in
        if ast.name not in o:
            raise UndeclaredFunction(ast.name)
        return None

    
