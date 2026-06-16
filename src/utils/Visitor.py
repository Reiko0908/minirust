from abc import ABC, abstractmethod
from typing import Any

class Visitor(ABC):
    def visit(self, ast, o: Any) -> Any:
        return ast.accept(self, o)

    @abstractmethod
    def visitProgram(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitStructDecl(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitFuncDecl(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitVarDecl(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitIntType(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitFloatType(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitBoolType(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitStringType(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitVoidType(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitArrayType(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitStructType(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitBlock(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitIf(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitWhile(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitFor(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitSwitch(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitCase(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitBreak(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitContinue(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitReturn(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitExprStmt(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitBinaryOp(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitUnaryOp(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitCallExpr(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitId(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitArrayCell(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitFieldAccess(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitStructInit(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitFieldInit(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitIntLiteral(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitFloatLiteral(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitBoolLiteral(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitStringLiteral(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitArrayLiteral(self, ast, o: Any) -> Any:
        pass

    @abstractmethod
    def visitAssign(self, ast, o: Any) -> Any:
        pass
class BaseVisitor(Visitor):
    def visitProgram(self, ast, o):
        return None
    def visitStructDecl(self, ast, o):
        return None
    def visitFuncDecl(self, ast, o):
        return None
    def visitVarDecl(self, ast, o):
        return None
    def visitIntType(self, ast, o):
        return None
    def visitFloatType(self, ast, o):
        return None
    def visitBoolType(self, ast, o):
        return None
    def visitStringType(self, ast, o):
        return None
    def visitVoidType(self, ast, o):
        return None
    def visitArrayType(self, ast, o):
        return None
    def visitStructType(self, ast, o):
        return None
    def visitBlock(self, ast, o):
        return None
    def visitIf(self, ast, o):
        return None
    def visitWhile(self, ast, o):
        return None
    def visitFor(self, ast, o):
        return None
    def visitSwitch(self, ast, o):
        return None
    def visitCase(self, ast, o):
        return None
    def visitBreak(self, ast, o):
        return None
    def visitContinue(self, ast, o):
        return None
    def visitReturn(self, ast, o):
        return None
    def visitExprStmt(self, ast, o):
        return None
    def visitBinaryOp(self, ast, o):
        return None
    def visitUnaryOp(self, ast, o):
        return None
    def visitCallExpr(self, ast, o):
        return None
    def visitId(self, ast, o):
        return None
    def visitArrayCell(self, ast, o):
        return None
    def visitFieldAccess(self, ast, o):
        return None
    def visitStructInit(self, ast, o):
        return None
    def visitFieldInit(self, ast, o):
        return None
    def visitIntLiteral(self, ast, o):
        return None
    def visitFloatLiteral(self, ast, o):
        return None
    def visitBoolLiteral(self, ast, o):
        return None
    def visitStringLiteral(self, ast, o):
        return None
    def visitArrayLiteral(self, ast, o):
        return None
    def visitAssign(self, ast, o):
        return None
