import os
import sys
from antlr4 import *

# Add grammar path to sys.path so we can import grammar classes cleanly
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "grammar"))

from MiniRustParser import MiniRustParser
from MiniRustVisitor import MiniRustVisitor
from utils.AST import *

class ASTGenerator(MiniRustVisitor):

    # ==============================================================
    # Program & Declarations
    # ==============================================================
    def visitProgram(self, ctx: MiniRustParser.ProgramContext):
        decls = [self.visit(s) for s in ctx.structDecl()]
        decls += [self.visit(f) for f in ctx.funcDecl()]
        return Program(decls)

    def visitStructDecl(self, ctx: MiniRustParser.StructDeclContext):
        name = ctx.ID().getText()
        fields = [self.visit(f) for f in ctx.fieldDecl()]
        return StructDecl(name, fields)

    def visitFieldDecl(self, ctx: MiniRustParser.FieldDeclContext):
        name = ctx.ID().getText()
        field_type = self.visit(ctx.typeName())
        return VarDecl(name, field_type, None, False)

    def visitFuncDecl(self, ctx: MiniRustParser.FuncDeclContext):
        name = ctx.ID().getText()
        params = []
        if ctx.paramList():
            params = [self.visit(p) for p in ctx.paramList().param()]
        return_type = self.visit(ctx.typeName()) if ctx.typeName() else VoidType()
        body = self.visit(ctx.block())
        return FuncDecl(name, params, return_type, body)

    def visitParamList(self, ctx: MiniRustParser.ParamListContext):
        return [self.visit(p) for p in ctx.param()]

    def visitParam(self, ctx: MiniRustParser.ParamContext):
        name = ctx.ID().getText()
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
        return StructType(ctx.ID().getText())

    _PRIMITIVE_TYPES_ = {
        'int'   : IntType(),
        'f32'   : FloatType(),
        'bool'  : BoolType(),
        'string': StringType(),
        'void'  : VoidType(),
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
        result = []
        for c in ctx.children:
            node = self.visit(c)
            if node is not None:
                result.append(node)
        return result

    def visitBlock(self, ctx: MiniRustParser.BlockContext):
        return Block(self._visit_body_items(ctx))

    def visitStmt(self, ctx: MiniRustParser.StmtContext):
        return self.visit(ctx.getChild(0))

    def visitVarDecl(self, ctx: MiniRustParser.VarDeclContext):
        name = ctx.ID().getText()
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
        body = self.visit(ctx.switchBody())
        cases_stmt = [self.visit(c) for c in body.caseClause()]
        default_stmt = self.visit(body.defaultClause()) if body.defaultClause() else None
        return Switch(expr, cases_stmt, default_stmt)
    
    def visitCaseClause(self, ctx: MiniRustParser.CaseClauseContext):
        expr = self.visit(ctx.literal())
        stmt = Block(self._visit_body_items(ctx))
        return Case(expr, stmt)
    
    def visitDefaultClause(self, ctx: MiniRustParser.DefaultClauseContext):
        return Block(self._visit_body_items(ctx))
    
    def visitWhileStmt(self, ctx: MiniRustParser.WhileStmtContext):
        cond = self.visit(ctx.expr())
        body = self.visit(ctx.block())
        return While(cond, body)

    def visitForStmt(self, ctx: MiniRustParser.ForStmtContext):
        var_name = ctx.ID().getText()
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
        result = Id(ctx.ID().getText())
        id_idx = 1
        expr_idx = 0
        for child in ctx.children[1:]:
            token = child.getText()
            if token == '.':
                result = FieldAccess(result, ctx.ID(id_idx).getText())
                id_idx += 1
            elif token == '[':
                result = ArrayCell(result, self.visit(ctx.expr(expr_idx)))
                expr_idx += 1
        return result
    
    def visitAssignExpr(self, ctx: MiniRustParser.AssignExprContext):
        if ctx.lvalue():
            lhs = self.visit(ctx.lvalue())
            rhs = self.visit(ctx.assignExpr())
            return Assign(lhs, rhs)
        return self.visit(ctx.orExpr())

    def _visitLeftAssoc(self,ctx):
        children = ctx.children
        result = self.visit(children[0])
        i = 1
        while i < len(children):
            op = children[i].getText()
            right = self.visit(children[i + 1])
            result = BinaryOp(op, result, right)
            i += 2
        return result

    def _visitNonAssoc(self,ctx, operand_accessor):
        operand = operand_accessor()
        left = self.visit(operand[0])
        if len(operand) == 1:
            return left
        right = self.visit(operand[1])
        op = ctx.getChild(1).getText()
        return BinaryOp(op, left, right) 

    def visitOrExpr(self, ctx: MiniRustParser.OrExprContext):
        return self._visitLeftAssoc(ctx)

    def visitAndExpr(self, ctx: MiniRustParser.AndExprContext):
        return self._visitLeftAssoc(ctx)

    def visitEqExpr(self, ctx: MiniRustParser.EqExprContext):
        return self._visitNonAssoc(ctx, ctx.relExpr)
    
    def visitRelExpr(self, ctx: MiniRustParser.RelExprContext):
        return self._visitNonAssoc(ctx, ctx.addExpr)

    def visitAddExpr(self, ctx: MiniRustParser.AddExprContext):
        return self._visitLeftAssoc(ctx)
    
    def visitMulExpr(self, ctx: MiniRustParser.MulExprContext):
        return self._visitLeftAssoc(ctx)

    def visitUnaryExpr(self, ctx: MiniRustParser.UnaryExprContext):
        result = self.visit(ctx.postfixExpr())
        for child in reversed(ctx.children[:-1]):
            result = UnaryOp(child.getText(), result)
        return result
     
    def visitPostfixExpr(self, ctx: MiniRustParser.PostfixExprContext):
        result = self.visit(ctx.primary())
        for op_ctx in ctx.postfixOp():
            if op_ctx.getChild(0).getText() == '.':
                result = FieldAccess(result, Id(op_ctx.ID().getText()))
            else:
                result = ArrayCell(result, self.visit(op_ctx.expr()))
        return result
    
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
        func_name = ctx.ID().getText()
        args = [self.visit(arg) for arg in ctx.argList().expr()] if ctx.argList() else []
        return CallExpr(func_name, args)
    
    def visitArgList(self, ctx: MiniRustParser.ArgListContext):
        return [self.visit(arg) for arg in ctx.expr()]

    def visitArrayLit(self, ctx: MiniRustParser.ArrayLitContext):
        elements = [self.visit(e) for e in ctx.expr()]
        return ArrayLiteral(elements)

    def visitStructInit(self, ctx: MiniRustParser.StructInitContext):
        struct_name = ctx.ID().getText()
        fields = [self.visit(f) for f in ctx.fieldInit()]
        return StructInit(struct_name, fields)
    
    def visitFieldInit(self,ctx: MiniRustParser.FieldInitContext):
        field_name = ctx.ID().getText()
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

