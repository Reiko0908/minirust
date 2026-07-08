import os
import sys
from functools import reduce

from antlr4 import *

# Add grammar path to sys.path so we can import grammar classes cleanly
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "grammar")
)

from MiniRustParser import MiniRustParser
from MiniRustVisitor import MiniRustVisitor

from utils.AST import *


class ASTGenerator(MiniRustVisitor):
    # ==============================================================
    # Program & Declarations
    # ==============================================================
    def visitProgram(self, ctx: MiniRustParser.ProgramContext):
        decls = list(map(self.visit, ctx.structDecl()))
        decls += list(map(self.visit, ctx.funcDecl()))
        return Program(decls)

    def visitStructDecl(self, ctx: MiniRustParser.StructDeclContext):
        name = Id(ctx.ID().getText())
        fields = list(map(self.visit, ctx.fieldDecl()))
        return StructDecl(name, fields)

    def visitFieldDecl(self, ctx: MiniRustParser.FieldDeclContext):
        name = Id(ctx.ID().getText())
        field_type = self.visit(ctx.typeName())
        return VarDecl(name, field_type, None, False)

    def visitFuncDecl(self, ctx: MiniRustParser.FuncDeclContext):
        name = Id(ctx.ID().getText())
        params = []
        if ctx.paramList():
            params = list(map(self.visit, ctx.paramList().param()))
        return_type = self.visit(ctx.typeName()) if ctx.typeName() else VoidType()
        body = self.visit(ctx.block())
        return FuncDecl(name, params, return_type, body)

    def visitParamList(self, ctx: MiniRustParser.ParamListContext):
        return list(map(self.visit, ctx.param()))

    def visitParam(self, ctx: MiniRustParser.ParamContext):
        name = Id(ctx.ID().getText())
        param_type = self.visit(ctx.typeName())
        return VarDecl(name, param_type, None, False)

    # ==============================================================
    # TypeNames
    # ==============================================================
    def visitTypeName(self, ctx: MiniRustParser.TypeNameContext):

        if ctx.primitiveType():
            return self.visit(ctx.primitiveType())
        elif ctx.arrayType():
            return self.visit(ctx.arrayType())
        return StructType(Id(ctx.ID().getText()))

    _PRIMITIVE_TYPES_ = {
        "i32": IntType(),
        "f32": FloatType(),
        "bool": BoolType(),
        "string": StringType(),
        "void": VoidType(),
    }

    def visitPrimitiveType(self, ctx: MiniRustParser.PrimitiveTypeContext):
        return self._PRIMITIVE_TYPES_[ctx.getText()]

    def visitArrayType(self, ctx: MiniRustParser.ArrayTypeContext):
        elem_type = self.visit(ctx.typeName())
        size = int(ctx.INT_LIT().getText())
        return ArrayType(elem_type, size)

    # ==============================================================
    # Blocks & Statements
    # ==============================================================
    def _visit_body_items(self, ctx):
        nodes = map(self.visit, ctx.children)
        return list(filter(lambda node: isinstance(node, (Stmt, VarDecl)), nodes))

    def visitBlock(self, ctx: MiniRustParser.BlockContext):
        return Block(self._visit_body_items(ctx))

    def visitStmt(self, ctx: MiniRustParser.StmtContext):
        return self.visit(ctx.getChild(0))

    def visitVarDecl(self, ctx: MiniRustParser.VarDeclContext):
        name = Id(ctx.ID().getText())
        mutable = ctx.MUT() is not None
        var_type = self.visit(ctx.typeName()) if ctx.typeName() else None
        init = self.visit(ctx.expr()) if ctx.expr() else None
        return VarDecl(name, var_type, init, mutable)

    def visitExprStmt(self, ctx: MiniRustParser.ExprStmtContext):
        return ExprStmt(self.visit(ctx.expr()))

    def visitIfStmt(self, ctx: MiniRustParser.IfStmtContext):
        cond = self.visit(ctx.expr())
        then_stmt = self.visit(ctx.block(0))
        else_stmt = None
        if ctx.ELSE():
            if ctx.ifStmt():
                else_stmt = self.visit(ctx.ifStmt())
            else:
                else_stmt = self.visit(ctx.block(1))
        return If(cond, then_stmt, else_stmt)

    def visitSwitchStmt(self, ctx: MiniRustParser.SwitchStmtContext):
        expr = self.visit(ctx.expr())
        body = ctx.switchBody()
        cases = list(map(self.visit, body.caseClause()))

        if body.defaultClause():
            cases.append(self.visit(body.defaultClause()))
        return Switch(expr, cases)

    def visitCaseClause(self, ctx: MiniRustParser.CaseClauseContext):
        val = self.visit(ctx.literal())
        body = self._visit_body_items(ctx)
        return Case(val, body)

    def visitDefaultClause(self, ctx: MiniRustParser.DefaultClauseContext):
        body = self._visit_body_items(ctx)
        return Case(None, body)

    def visitWhileStmt(self, ctx: MiniRustParser.WhileStmtContext):
        cond = self.visit(ctx.expr())
        body = self.visit(ctx.block())
        return While(cond, body)

    def visitForStmt(self, ctx: MiniRustParser.ForStmtContext):
        var_name = Id(ctx.ID().getText())
        start = self.visit(ctx.expr(0))
        end = self.visit(ctx.expr(1))
        body = self.visit(ctx.block())
        return For(var_name, start, end, body)

    def visitBreakStmt(self, ctx: MiniRustParser.BreakStmtContext):
        return Break()

    def visitContinueStmt(self, ctx: MiniRustParser.ContinueStmtContext):
        return Continue()

    def visitReturnStmt(self, ctx: MiniRustParser.ReturnStmtContext):
        expr = self.visit(ctx.expr()) if ctx.expr() else None
        return Return(expr)

    # ==============================================================
    # Expressions
    # ==============================================================
    def visitExpr(self, ctx: MiniRustParser.ExprContext):
        return self.visit(ctx.assignExpr())

    def visitLvalue(self, ctx: MiniRustParser.LvalueContext):
        ids = iter(ctx.ID()[1:])
        exprs = iter(ctx.expr())

        def step(acc, child):
            token = child.getText()
            if token == ".":
                return FieldAccess(acc, Id(next(ids).getText()))
            if token == "[":
                return ArrayCell(acc, self.visit(next(exprs)))
            return acc

        return reduce(step, ctx.children[1:], Id(ctx.ID(0).getText()))

    def visitAssignExpr(self, ctx: MiniRustParser.AssignExprContext):
        if ctx.lvalue():
            lhs = self.visit(ctx.lvalue())
            rhs = self.visit(ctx.assignExpr())
            return Assign(lhs, rhs)
        return self.visit(ctx.orExpr())

    def _visitLeftAssoc(self, ctx):
        ops = ctx.children[1::2]
        operands = ctx.children[2::2]
        return reduce(
            lambda acc, pair: BinaryOp(pair[0].getText(), acc, self.visit(pair[1])),
            zip(ops, operands),
            self.visit(ctx.children[0]),
        )

    def _visitNonAssoc(self, ctx):
        left = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return left
        op = ctx.children[1].getText()
        right = self.visit(ctx.children[2])
        return BinaryOp(op, left, right)

    def visitOrExpr(self, ctx: MiniRustParser.OrExprContext):
        return self._visitLeftAssoc(ctx)

    def visitAndExpr(self, ctx: MiniRustParser.AndExprContext):
        return self._visitLeftAssoc(ctx)

    def visitEqExpr(self, ctx: MiniRustParser.EqExprContext):
        return self._visitNonAssoc(ctx)

    def visitRelExpr(self, ctx: MiniRustParser.RelExprContext):
        return self._visitNonAssoc(ctx)

    def visitAddExpr(self, ctx: MiniRustParser.AddExprContext):
        return self._visitLeftAssoc(ctx)

    def visitMulExpr(self, ctx: MiniRustParser.MulExprContext):
        return self._visitLeftAssoc(ctx)

    def visitUnaryExpr(self, ctx: MiniRustParser.UnaryExprContext):
        result = self.visit(ctx.postfixExpr())
        ops = ctx.children[:-1][::-1]
        return reduce(lambda acc, op: UnaryOp(op.getText(), acc), ops, result)

    def visitPostfixExpr(self, ctx: MiniRustParser.PostfixExprContext):
        def _visitPostfixOp(acc, op):
            if op.ID():
                return FieldAccess(acc, Id(op.ID().getText()))
            return ArrayCell(acc, self.visit(op.expr()))

        return reduce(_visitPostfixOp, ctx.postfixOp(), self.visit(ctx.primary()))

    def visitPrimary(self, ctx: MiniRustParser.PrimaryContext):
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.arrayLit():
            return self.visit(ctx.arrayLit())
        elif ctx.structInit():
            return self.visit(ctx.structInit())
        elif ctx.callExpr():
            return self.visit(ctx.callExpr())
        elif ctx.ID() is not None:
            return Id(ctx.ID().getText())
        return self.visit(ctx.expr())

    def visitCallExpr(self, ctx: MiniRustParser.CallExprContext):
        func_name = Id(ctx.ID().getText())
        args = list(map(self.visit, ctx.argList().expr())) if ctx.argList() else []
        return CallExpr(func_name, args)

    def visitArgList(self, ctx: MiniRustParser.ArgListContext):
        return list(map(self.visit, ctx.expr()))

    def visitArrayLit(self, ctx: MiniRustParser.ArrayLitContext):
        elements = list(map(self.visit, ctx.expr()))
        return ArrayLiteral(elements)

    def visitStructInit(self, ctx: MiniRustParser.StructInitContext):
        struct_name = Id(ctx.ID().getText())
        fields = list(map(self.visit, ctx.fieldInit()))
        return StructInit(struct_name, fields)

    def visitFieldInit(self, ctx: MiniRustParser.FieldInitContext):
        field_name = Id(ctx.ID().getText())
        expr = self.visit(ctx.expr())
        return FieldInit(field_name, expr)

    # ==============================================================
    # Literals
    # ==============================================================
    def visitLiteral(self, ctx: MiniRustParser.LiteralContext):
        if ctx.INT_LIT():
            return IntLiteral(int(ctx.INT_LIT().getText()))
        elif ctx.FLOAT_LIT():
            return FloatLiteral(float(ctx.FLOAT_LIT().getText()))
        elif ctx.STRING_LIT():
            return StringLiteral(ctx.STRING_LIT().getText())
        elif ctx.TRUE():
            return BoolLiteral(True)
        return BoolLiteral(False)
