import sys
import os
import inspect
from antlr4 import *

# Add source directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from TestUtils import TestAST

def check_ast(input_str, expected_str):
    func_name = inspect.stack()[1].function
    test_num = func_name.split('_')[1]
    TestAST.checkAST(input_str, expected_str)

def test_300():
    # Sample test: Minimum program
    check_ast(
        "fn main() { print_i32(1); }",
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(CallExpr(Id(print_i32), [IntLiteral(1)]))]))])"
    )

# TODO: Add more test cases (from test_301 to test_399) to complete the 100 test suite
# after extending the grammar (MiniRust.g4) and the ASTGenerator.py.
