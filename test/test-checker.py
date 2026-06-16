import pytest
from checker.StaticChecker import StaticChecker
from checker.StaticError import *
from TestUtils import TestChecker
from utils.AST import *


def test_401():
    source = "fn main() {pprint(1);}"  # pprint is not a built‑in
    # Use TestChecker utility to run the check and expect the full error message
    TestChecker.checkChecker(source, "UndeclaredFunction(pprint)")


def test_402():
    ast_obj = Program([FuncDecl(Id("main"), [], VoidType, Block([ExprStmt(CallExpr(Id("pprint"), [IntLiteral(1)]))]))])
    # Use TestChecker with AST input
    TestChecker.checkChecker(ast_obj, "UndeclaredFunction(Id(pprint))")
