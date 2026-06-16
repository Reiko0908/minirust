import sys
import os
from antlr4 import *

# Add grammar path to sys.path so we can import grammar classes cleanly
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "grammar"))

from MiniRustVisitor import MiniRustVisitor
from MiniRustParser import MiniRustParser
from utils.AST import *

class ASTGenerator(MiniRustVisitor):

    def visitProgram(self, ctx: MiniRustParser.ProgramContext):
        return Program([self.visit(ctx.funcDecl())])

    def visitFuncDecl(self, ctx: MiniRustParser.FuncDeclContext):
        name = ctx.ID().getText()
        params = []
        return_type = VoidType()
        body = self.visit(ctx.block())
        return FuncDecl(name, params, return_type, body)

    def visitBlock(self, ctx: MiniRustParser.BlockContext):
        stmt = self.visit(ctx.statement())
        return Block([stmt])

    def visitStatement(self, ctx: MiniRustParser.StatementContext):
        expr = self.visit(ctx.callExpr())
        return ExprStmt(expr)

    # Handle call expressions
    def visitCallExpr(self, ctx: MiniRustParser.CallExprContext):
        name = ctx.ID().getText()
        # argument is an expression (int literal or nested call)
        val = int(ctx.INT_LIT().getText())
        arg = IntLiteral(val)
        return CallExpr(name, [arg])

        
