import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from utils.AST import *
from TestUtils import CodeGenerator

def test_001():
    """Test 1: Minimal main printing 1 using raw source string"""
    raw_code = "fn main() { print_i32(1); }"
    expected = "1"
    result = CodeGenerator().generate_and_run(raw_code)
    assert result == expected, f"Expected '{expected}', got '{result}'"

def test_002():
    """Test 2: Minimal main printing 1 using AST format"""
    ast = Program([
        FuncDecl(
            "main",
            [],
            VoidType(),
            Block([
                ExprStmt(CallExpr("print_i32", [IntLiteral(1)]))
            ])
        )
    ])
    expected = "1"
    result = CodeGenerator().generate_and_run(ast)
    assert result == expected, f"Expected '{expected}', got '{result}'"
