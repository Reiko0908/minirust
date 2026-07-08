import inspect
import os
import sys

from antlr4 import *

# Add source directory to path
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)

from TestUtils import TestAST


def check_ast(input_str, expected_str):
    func_name = inspect.stack()[1].function
    test_num = func_name.split("_")[1]
    TestAST.checkAST(input_str, expected_str)


# =============================================================================
# Group 1: Declarations & Definitions (test_301 - test_308)
# =============================================================================
def test_301():
    # Struct declaration with multiple fields
    check_ast(
        r"""
        struct Point {
            x: i32, y: i32
        }
        """,
        "Program([StructDecl(Id(Point), [VarDecl(Id(x), IntType, None, False), "
        "VarDecl(Id(y), IntType, None, False)])])",
    )


def test_302():
    # Function returning void (no arrow) vs typed return
    check_ast(
        r"""
        fn greet() { }
        fn add(a: i32, b: i32) -> i32 {
            return a + b;
        }
        """,
        "Program([FuncDecl(Id(greet), [], VoidType, Block([])), "
        "FuncDecl(Id(add), [VarDecl(Id(a), IntType, None, False), "
        "VarDecl(Id(b), IntType, None, False)], IntType, "
        "Block([Return(BinaryOp('+', Id(a), Id(b)))]))])",
    )


def test_303():
    # Struct used as a parameter and return type
    check_ast(
        r"""
        struct Point {
            x: i32, y: i32
        }
        fn identity(p: Point) -> Point {
            return p;
        }
        """,
        "Program([StructDecl(Id(Point), [VarDecl(Id(x), IntType, None, False), "
        "VarDecl(Id(y), IntType, None, False)]), "
        "FuncDecl(Id(identity), [VarDecl(Id(p), StructType(Id(Point)), None, False)], "
        "StructType(Id(Point)), Block([Return(Id(p))]))])",
    )


def test_304():
    # let with explicit type and initializer
    check_ast(
        r"""
        fn main() {
            let x: i32 = 5;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([VarDecl(Id(x), IntType, IntLiteral(5), False)]))])",
    )


def test_305():
    # let mut with explicit type and initializer
    check_ast(
        r"""
        fn main() {
            let mut x: f32 = 1.5;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([VarDecl(Id(x), FloatType, FloatLiteral(1.5), True)]))])",
    )


def test_306():
    # let with local type inference (no explicit type annotation)
    check_ast(
        r"""
        fn main() {
            let x = 5;
            let mut y = true;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([VarDecl(Id(x), None, IntLiteral(5), False), "
        "VarDecl(Id(y), None, BoolLiteral(True), True)]))])",
    )


def test_307():
    # mutable uninitialized variable declaration (requires mut + type, no init)
    check_ast(
        r"""
        fn main() {
            let mut x: i32;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([VarDecl(Id(x), IntType, None, True)]))])",
    )


def test_308():
    # Multiple struct declarations followed by multiple function declarations
    check_ast(
        r"""
        struct A {
            v: i32
        }
        struct B {
            v: f32
        }
        fn main() {
        }
        """,
        "Program([StructDecl(Id(A), [VarDecl(Id(v), IntType, None, False)]), "
        "StructDecl(Id(B), [VarDecl(Id(v), FloatType, None, False)]), "
        "FuncDecl(Id(main), [], VoidType, Block([]))])",
    )


def test_309():
    # Struct containing another struct as a field
    check_ast(
        r"""
        struct Point {
            x: i32, y: i32
        }

        struct Line {
            start: Point, end: Point
        }
        """,
        "Program([StructDecl(Id(Point), [VarDecl(Id(x), IntType, None, False), "
        "VarDecl(Id(y), IntType, None, False)]), "
        "StructDecl(Id(Line), [VarDecl(Id(start), StructType(Id(Point)), None, False), "
        "VarDecl(Id(end), StructType(Id(Point)), None, False)])])",
    )


# =============================================================================
# Group 2: Control Flow (test_309 - test_321)
# =============================================================================
def test_310():
    # Simple if without else
    check_ast(
        r"""
        fn main() {
            if x > 0 {
                y = 1;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([If(BinaryOp('>', Id(x), IntLiteral(0)), "
        "Block([ExprStmt(Assign(Id(y), IntLiteral(1)))]), None)]))])",
    )


def test_311():
    # if / else
    check_ast(
        r"""
        fn main() {
            if x > 0 {
                y = 1;
            }
            else {
                y = -1;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([If(BinaryOp('>', Id(x), IntLiteral(0)), "
        "Block([ExprStmt(Assign(Id(y), IntLiteral(1)))]), "
        "Block([ExprStmt(Assign(Id(y), UnaryOp('-', IntLiteral(1))))]))]))])",
    )


def test_312():
    # Deeply nested if-else-if chain
    check_ast(
        r"""
        fn main() {
            if x > 0 {
                y = 1;
            }
            else if x < 0 {
                y = -1;
            }
            else {
                y = 0;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([If(BinaryOp('>', Id(x), IntLiteral(0)), "
        "Block([ExprStmt(Assign(Id(y), IntLiteral(1)))]), "
        "If(BinaryOp('<', Id(x), IntLiteral(0)), "
        "Block([ExprStmt(Assign(Id(y), UnaryOp('-', IntLiteral(1))))]), "
        "Block([ExprStmt(Assign(Id(y), IntLiteral(0)))])))]))])",
    )


def test_313():
    # while loop
    check_ast(
        r"""
        fn main() {
            while x < 10 {
                x = x + 1;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([While(BinaryOp('<', Id(x), IntLiteral(10)), "
        "Block([ExprStmt(Assign(Id(x), BinaryOp('+', Id(x), IntLiteral(1))))]))]))])",
    )


def test_314():
    # for-in range loop
    check_ast(
        r"""
        fn main() {
            for i in 0..10 {
                x = x + i;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([For(Id(i), IntLiteral(0), IntLiteral(10), "
        "Block([ExprStmt(Assign(Id(x), BinaryOp('+', Id(x), Id(i))))]))]))])",
    )


def test_315():
    # for-in with variable bounds
    check_ast(
        r"""
        fn main() {
            for i in start..end {
                total = total + i;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([For(Id(i), Id(start), Id(end), "
        "Block([ExprStmt(Assign(Id(total), BinaryOp('+', Id(total), Id(i))))]))]))])",
    )


def test_316():
    # break inside while
    check_ast(
        r"""
        fn main() {
            while true {
                break;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([While(BoolLiteral(True), Block([Break()]))]))])",
    )


def test_317():
    # continue inside for
    check_ast(
        r"""
        fn main() {
            for i in 0..5 {
                continue;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([For(Id(i), IntLiteral(0), IntLiteral(5), Block([Continue()]))]))])",
    )


def test_318():
    # break/continue combined with nested if conditions
    check_ast(
        r"""
        fn main() {
            while x < 10 {
                if x == 5 {
                    continue;
                }
                if x == 9 {
                    break;
                }
                x = x + 1;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([While(BinaryOp('<', Id(x), IntLiteral(10)), Block(["
        "If(BinaryOp('==', Id(x), IntLiteral(5)), Block([Continue()]), None), "
        "If(BinaryOp('==', Id(x), IntLiteral(9)), Block([Break()]), None), "
        "ExprStmt(Assign(Id(x), BinaryOp('+', Id(x), IntLiteral(1))))]))]))])",
    )


def test_319():
    # return without a value
    check_ast(
        r"""
        fn foo() {
            return;
        }
        """,
        "Program([FuncDecl(Id(foo), [], VoidType, Block([Return(None)]))])",
    )


def test_320():
    # return with a value
    check_ast(
        r"""
        fn foo() -> i32 {
            return 42;
        }
        """,
        "Program([FuncDecl(Id(foo), [], IntType, Block([Return(IntLiteral(42))]))])",
    )


def test_321():
    # Nested lexical blocks (bare braces) inside a function body
    check_ast(
        r"""
        fn main() {
            {
                let x = 1;
                {
                    let y = 2;
                }
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([Block(["
        "VarDecl(Id(x), None, IntLiteral(1), False), "
        "Block([VarDecl(Id(y), None, IntLiteral(2), False)])])]))])",
    )


def test_322():
    # if condition contains a nested block as the then branch with multiple statements
    check_ast(
        r"""
        fn main() {
            if flag {
                let a = 1;
                let b = 2;
                a = b;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([If(Id(flag), Block(["
        "VarDecl(Id(a), None, IntLiteral(1), False), "
        "VarDecl(Id(b), None, IntLiteral(2), False), "
        "ExprStmt(Assign(Id(a), Id(b)))]), None)]))])",
    )


# =============================================================================
# Group 3: Switch Statement, C-style (test_322 - test_326)
# =============================================================================
def test_323():
    # switch with multiple cases and a default clause
    check_ast(
        r"""
        fn main() {
            switch x {
                case 1: y = 1;
                case 2: y = 2;
                default: y = 0;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([Switch(Id(x), ["
        "Case(IntLiteral(1), [ExprStmt(Assign(Id(y), IntLiteral(1)))]), "
        "Case(IntLiteral(2), [ExprStmt(Assign(Id(y), IntLiteral(2)))]), "
        "Case(None, [ExprStmt(Assign(Id(y), IntLiteral(0)))])"
        "])]))])",
    )


def test_324():
    # switch with no default clause (default is optional)
    check_ast(
        r"""
        fn main() {
            switch x {
                case 1: y = 1;
                case 2: y = 2;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([Switch(Id(x), ["
        "Case(IntLiteral(1), [ExprStmt(Assign(Id(y), IntLiteral(1)))]), "
        "Case(IntLiteral(2), [ExprStmt(Assign(Id(y), IntLiteral(2)))])"
        "])]))])",
    )


def test_325():
    # fall-through chain: case 1: case 2: shares the body of case 2
    check_ast(
        r"""
        fn main() {
            switch x {
                case 1: case 2: y = 1;
                default: y = 0;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([Switch(Id(x), ["
        "Case(IntLiteral(1), []), "
        "Case(IntLiteral(2), [ExprStmt(Assign(Id(y), IntLiteral(1)))]), "
        "Case(None, [ExprStmt(Assign(Id(y), IntLiteral(0)))])"
        "])]))])",
    )


def test_326():
    # nested lexical block inside a case clause
    check_ast(
        r"""
        fn main() {
            switch x {
                case 1: {
                    let z = 1;
                    y = z;
                }
                default: y = 0;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([Switch(Id(x), ["
        "Case(IntLiteral(1), [Block([VarDecl(Id(z), None, IntLiteral(1), False), "
        "ExprStmt(Assign(Id(y), Id(z)))])]), "
        "Case(None, [ExprStmt(Assign(Id(y), IntLiteral(0)))])"
        "])]))])",
    )


def test_327():
    # switch scrutinee is a logical/relational expression, case values are bool literals
    check_ast(
        r"""
        fn main() {
            switch (a > b) {
                case true: y = 1;
                default: y = 0;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([Switch(BinaryOp('>', Id(a), Id(b)), ["
        "Case(BoolLiteral(True), [ExprStmt(Assign(Id(y), IntLiteral(1)))]), "
        "Case(None, [ExprStmt(Assign(Id(y), IntLiteral(0)))])"
        "])]))])",
    )


# =============================================================================
# Group 4: Arrays & Struct Instantiation (test_327 - test_336)
# =============================================================================
def test_328():
    # Simple array declaration with array literal
    check_ast(
        r"""
        fn main() {
            let arr: [i32; 3] = [1, 2, 3];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([VarDecl(Id(arr), "
        "ArrayType(IntType, 3), ArrayLiteral([IntLiteral(1), IntLiteral(2), "
        "IntLiteral(3)]), False)]))])",
    )


def test_329():
    # Multidimensional array type and literal
    check_ast(
        r"""
        fn main() {
            let m: [[i32; 2]; 3] = [[1,2],[3,4],[5,6]];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([VarDecl(Id(m), "
        "ArrayType(ArrayType(IntType, 2), 3), ArrayLiteral(["
        "ArrayLiteral([IntLiteral(1), IntLiteral(2)]), "
        "ArrayLiteral([IntLiteral(3), IntLiteral(4)]), "
        "ArrayLiteral([IntLiteral(5), IntLiteral(6)])]), False)]))])",
    )


def test_330():
    # Empty array literal
    check_ast(
        r"""
        fn main() {
            let a: [i32; 0] = [];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([VarDecl(Id(a), "
        "ArrayType(IntType, 0), ArrayLiteral([]), False)]))])",
    )


def test_331():
    # Single and chained array indexing
    check_ast(
        r"""
        fn main() {
            x = arr[0];
            y = matrix[0][1];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), ArrayCell(Id(arr), IntLiteral(0)))), "
        "ExprStmt(Assign(Id(y), ArrayCell(ArrayCell(Id(matrix), IntLiteral(0)), IntLiteral(1))))]))])",
    )


def test_332():
    # Simple struct instantiation
    check_ast(
        r"""
        fn main() {
            let p = Point {
                x: 1, y: 2
            };
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([VarDecl(Id(p), None, "
        "StructInit(Id(Point), [FieldInit(Id(x), IntLiteral(1)), "
        "FieldInit(Id(y), IntLiteral(2))]), False)]))])",
    )


def test_333():
    # Struct instantiation with a nested struct-typed field initializer
    check_ast(
        r"""
        fn main() {
            let l = Line {
                start: Point {
                    x: 1, y: 2
                }
                , end: Point {
                    x: 3, y: 4
                }
            };
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([VarDecl(Id(l), None, "
        "StructInit(Id(Line), ["
        "FieldInit(Id(start), StructInit(Id(Point), [FieldInit(Id(x), IntLiteral(1)), "
        "FieldInit(Id(y), IntLiteral(2))])), "
        "FieldInit(Id(end), StructInit(Id(Point), [FieldInit(Id(x), IntLiteral(3)), "
        "FieldInit(Id(y), IntLiteral(4))]))]), False)]))])",
    )


def test_334():
    # Field access, including chained field access
    check_ast(
        r"""
        fn main() {
            x = p.x;
            y = p.pos.x;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), FieldAccess(Id(p), Id(x)))), "
        "ExprStmt(Assign(Id(y), FieldAccess(FieldAccess(Id(p), Id(pos)), Id(x))))]))])",
    )


def test_335():
    # Boundary mixing: field access on an array cell, and array cell on a field access
    check_ast(
        r"""
        fn main() {
            x = points[0].x;
            y = shapes[i].vertices[j];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), FieldAccess(ArrayCell(Id(points), IntLiteral(0)), Id(x)))), "
        "ExprStmt(Assign(Id(y), ArrayCell(FieldAccess(ArrayCell(Id(shapes), Id(i)), "
        "Id(vertices)), Id(j))))]))])",
    )


def test_336():
    # Array literal whose elements are arbitrary expressions
    check_ast(
        r"""
        fn main() {
            let a: [i32; 3] = [x + 1, y * 2, z];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([VarDecl(Id(a), "
        "ArrayType(IntType, 3), ArrayLiteral(["
        "BinaryOp('+', Id(x), IntLiteral(1)), BinaryOp('*', Id(y), IntLiteral(2)), "
        "Id(z)]), False)]))])",
    )


def test_337():
    # Struct with an array-typed field, instantiated with an array literal
    check_ast(
        r"""
        struct Grid {
            cells: [i32; 4]
        }
        fn main() {
            let g = Grid {
                cells: [0,0,0,0]
            };
        }
        """,
        "Program([StructDecl(Id(Grid), [VarDecl(Id(cells), ArrayType(IntType, 4), None, False)]), "
        "FuncDecl(Id(main), [], VoidType, Block([VarDecl(Id(g), None, "
        "StructInit(Id(Grid), [FieldInit(Id(cells), ArrayLiteral(["
        "IntLiteral(0), IntLiteral(0), IntLiteral(0), IntLiteral(0)]))]), False)]))])",
    )


# =============================================================================
# Group 5: Literals & Escape Sequences (test_337 - test_346)
# =============================================================================
def test_338():
    # Boolean literals
    check_ast(
        r"""
        fn main() {
            x = true;
            y = false;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BoolLiteral(True))), "
        "ExprStmt(Assign(Id(y), BoolLiteral(False)))]))])",
    )


def test_339():
    # Floating-point scientific/exponential notation
    check_ast(
        r"""
        fn main() {
            x = 1.5e10;
            y = 2.0E-3;
            z = 3e5;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), FloatLiteral(15000000000.0))), "
        "ExprStmt(Assign(Id(y), FloatLiteral(0.002))), "
        "ExprStmt(Assign(Id(z), FloatLiteral(300000.0)))]))])",
    )


def test_340():
    # \n escape sequence
    check_ast(
        r"""
        fn main() {
            x = "hello\nworld";
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        'ExprStmt(Assign(Id(x), StringLiteral("hello\\nworld")))]))])',
    )


def test_341():
    # \t escape sequence
    check_ast(
        r"""
        fn main() {
            x = "col1\tcol2";
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        'ExprStmt(Assign(Id(x), StringLiteral("col1\\tcol2")))]))])',
    )


def test_342():
    # \" escape sequence
    check_ast(
        r"""
        fn main() {
            x = "she said \"hi\"";
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        'ExprStmt(Assign(Id(x), StringLiteral("she said \\"hi\\"")))]))])',
    )


def test_343():
    # \\ escape sequence
    check_ast(
        r"""
        fn main() {
            x = "C:\\path\\file";
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        'ExprStmt(Assign(Id(x), StringLiteral("C:\\\\path\\\\file")))]))])',
    )


def test_344():
    # Nested/combined escape sequences within one string
    check_ast(
        r"""
        fn main() {
            x = "line1\nline2\ttabbed \"quoted\" \\end";
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), StringLiteral("
        '"line1\\nline2\\ttabbed \\"quoted\\" \\\\end")))]))])',
    )


def test_345():
    # Plain string literal with no escapes
    check_ast(
        r"""
        fn main() {
            x = "plain string";
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        'ExprStmt(Assign(Id(x), StringLiteral("plain string")))]))])',
    )


def test_346():
    # Negative int/float literals via unary minus
    check_ast(
        r"""
        fn main() {
            x = -3.14;
            y = -100;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), UnaryOp('-', FloatLiteral(3.14)))), "
        "ExprStmt(Assign(Id(y), UnaryOp('-', IntLiteral(100))))]))])",
    )


def test_347():
    # Boolean literals inside an array literal, and a string field in struct init
    check_ast(
        r"""
        struct Msg {
            text: string
        }
        fn main() {
            let flags: [bool; 2] = [true, false];
            let m = Msg {
                text: "hi\n"
            };
        }
        """,
        "Program([StructDecl(Id(Msg), [VarDecl(Id(text), StringType, None, False)]), "
        "FuncDecl(Id(main), [], VoidType, Block(["
        "VarDecl(Id(flags), ArrayType(BoolType, 2), "
        "ArrayLiteral([BoolLiteral(True), BoolLiteral(False)]), False), "
        "VarDecl(Id(m), None, StructInit(Id(Msg), "
        '[FieldInit(Id(text), StringLiteral("hi\\n"))]), False)]))])',
    )


# =============================================================================
# Group 6: Function Calls & Return (test_347 - test_351)
# =============================================================================
def test_348():
    # Library function invocations with a single argument each
    check_ast(
        r"""
        fn main() {
            print_i32(1);
            print_str("hi");
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(CallExpr(Id(print_i32), [IntLiteral(1)])), "
        'ExprStmt(CallExpr(Id(print_str), [StringLiteral("hi")]))]))])',
    )


def test_349():
    # Function call with no arguments
    check_ast(
        r"""
        fn main() {
            flush();
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, "
        "Block([ExprStmt(CallExpr(Id(flush), []))]))])",
    )


def test_350():
    # Multi-argument call with a nested call as an argument
    check_ast(
        r"""
        fn main() {
            x = add(mul(2, 3), 4);
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "CallExpr(Id(add), [CallExpr(Id(mul), [IntLiteral(2), IntLiteral(3)]), "
        "IntLiteral(4)])))]))])",
    )


def test_351():
    # Return carrying a call expression (with a nested call argument)
    check_ast(
        r"""
        fn compute() -> i32 {
            return add(1, mul(2, 3));
        }
        """,
        "Program([FuncDecl(Id(compute), [], IntType, Block([Return("
        "CallExpr(Id(add), [IntLiteral(1), CallExpr(Id(mul), "
        "[IntLiteral(2), IntLiteral(3)])]))]))])",
    )


def test_352():
    # Return carrying a complex arithmetic expression
    check_ast(
        r"""
        fn compute(a: i32, b: i32) -> i32 {
            return a * b + (a - b) / 2;
        }
        """,
        "Program([FuncDecl(Id(compute), [VarDecl(Id(a), IntType, None, False), "
        "VarDecl(Id(b), IntType, None, False)], IntType, Block([Return("
        "BinaryOp('+', BinaryOp('*', Id(a), Id(b)), "
        "BinaryOp('/', BinaryOp('-', Id(a), Id(b)), IntLiteral(2))))]))])",
    )


# =============================================================================
# Group 7: Operators & Precedence (test_352 - test_380)
# =============================================================================
def test_353():
    # Unary minus and unary not
    check_ast(
        r"""
        fn main() {
            x = -a;
            y = !b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), UnaryOp('-', Id(a)))), "
        "ExprStmt(Assign(Id(y), UnaryOp('!', Id(b))))]))])",
    )


def test_354():
    # Chained/stacked unary operators
    check_ast(
        r"""
        fn main() {
            x = -!a;
            y = !!b;
            z = --c;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), UnaryOp('-', UnaryOp('!', Id(a))))), "
        "ExprStmt(Assign(Id(y), UnaryOp('!', UnaryOp('!', Id(b))))), "
        "ExprStmt(Assign(Id(z), UnaryOp('-', UnaryOp('-', Id(c)))))]))])",
    )


def test_355():
    # Multiplicative operators are left-associative and share precedence
    check_ast(
        r"""
        fn main() {
            x = a * b / c % d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('%', BinaryOp('/', BinaryOp('*', Id(a), Id(b)), Id(c)), Id(d))))]))])",
    )


def test_356():
    # Additive operators are left-associative
    check_ast(
        r"""
        fn main() {
            x = a + b - c + d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('+', BinaryOp('-', BinaryOp('+', Id(a), Id(b)), Id(c)), Id(d))))]))])",
    )


def test_357():
    # Multiplicative binds tighter than additive
    check_ast(
        r"""
        fn main() {
            x = a + b * c;
            y = a * b + c;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BinaryOp('+', Id(a), BinaryOp('*', Id(b), Id(c))))), "
        "ExprStmt(Assign(Id(y), BinaryOp('+', BinaryOp('*', Id(a), Id(b)), Id(c))))]))])",
    )


def test_358():
    # Parentheses override default precedence
    check_ast(
        r"""
        fn main() {
            x = (a + b) * c;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('*', BinaryOp('+', Id(a), Id(b)), Id(c))))]))])",
    )


def test_359():
    # Equality operators (non-associative, single application)
    check_ast(
        r"""
        fn main() {
            x = a == b;
            y = a != b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BinaryOp('==', Id(a), Id(b)))), "
        "ExprStmt(Assign(Id(y), BinaryOp('!=', Id(a), Id(b))))]))])",
    )


def test_360():
    # All four relational operators
    check_ast(
        r"""
        fn main() {
            x = a < b;
            y = a <= b;
            z = a > b;
            w = a >= b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BinaryOp('<', Id(a), Id(b)))), "
        "ExprStmt(Assign(Id(y), BinaryOp('<=', Id(a), Id(b)))), "
        "ExprStmt(Assign(Id(z), BinaryOp('>', Id(a), Id(b)))), "
        "ExprStmt(Assign(Id(w), BinaryOp('>=', Id(a), Id(b))))]))])",
    )


def test_361():
    # Relational binds tighter than equality
    check_ast(
        r"""
        fn main() {
            x = a < b == c > d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('==', BinaryOp('<', Id(a), Id(b)), BinaryOp('>', Id(c), Id(d)))))]))])",
    )


def test_362():
    # Additive binds tighter than relational
    check_ast(
        r"""
        fn main() {
            x = a + 1 < b - 1;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('<', BinaryOp('+', Id(a), IntLiteral(1)), "
        "BinaryOp('-', Id(b), IntLiteral(1)))))]))])",
    )


def test_363():
    # Logical AND and OR
    check_ast(
        r"""
        fn main() {
            x = a && b;
            y = a || b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BinaryOp('&&', Id(a), Id(b)))), "
        "ExprStmt(Assign(Id(y), BinaryOp('||', Id(a), Id(b))))]))])",
    )


def test_364():
    # AND binds tighter than OR
    check_ast(
        r"""
        fn main() {
            x = a && b || c;
            y = a || b && c;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BinaryOp('||', BinaryOp('&&', Id(a), Id(b)), Id(c)))), "
        "ExprStmt(Assign(Id(y), BinaryOp('||', Id(a), BinaryOp('&&', Id(b), Id(c)))))]))])",
    )


def test_365():
    # Relational binds tighter than logical AND
    check_ast(
        r"""
        fn main() {
            x = a < b && c > d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('&&', BinaryOp('<', Id(a), Id(b)), BinaryOp('>', Id(c), Id(d)))))]))])",
    )


def test_366():
    # Full ladder mixed together: equality/relational under AND under OR
    check_ast(
        r"""
        fn main() {
            x = a == b && c != d || e;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('||', BinaryOp('&&', BinaryOp('==', Id(a), Id(b)), "
        "BinaryOp('!=', Id(c), Id(d))), Id(e))))]))])",
    )


def test_367():
    # Simple right-associative assignment
    check_ast(
        r"""
        fn main() {
            x = a = b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "Assign(Id(a), Id(b))))]))])",
    )


def test_368():
    # Assignment chain of three
    check_ast(
        r"""
        fn main() {
            x = y = z = 5;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "Assign(Id(y), Assign(Id(z), IntLiteral(5)))))]))])",
    )


def test_369():
    # Unary not combined with logical AND
    check_ast(
        r"""
        fn main() {
            x = !a && !b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('&&', UnaryOp('!', Id(a)), UnaryOp('!', Id(b)))))]))])",
    )


def test_370():
    # Unary minus binds tighter than additive; parens override it
    check_ast(
        r"""
        fn main() {
            x = -a + b;
            y = -(a + b);
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BinaryOp('+', UnaryOp('-', Id(a)), Id(b)))), "
        "ExprStmt(Assign(Id(y), UnaryOp('-', BinaryOp('+', Id(a), Id(b)))))]))])",
    )


def test_371():
    # Binary minus followed by unary minus operand
    check_ast(
        r"""
        fn main() {
            x = a - -b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('-', Id(a), UnaryOp('-', Id(b)))))]))])",
    )


def test_372():
    # Assignment target is a field access (member assignment chain)
    check_ast(
        r"""
        fn main() {
            a.b = c.d = 5;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign("
        "FieldAccess(Id(a), Id(b)), Assign(FieldAccess(Id(c), Id(d)), IntLiteral(5))))]))])",
    )


def test_373():
    # Parenthesized assignment used as a sub-expression
    check_ast(
        r"""
        fn main() {
            x = (a = b) + 1;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('+', Assign(Id(a), Id(b)), IntLiteral(1))))]))])",
    )


def test_374():
    # Multiplicative and unary combined
    check_ast(
        r"""
        fn main() {
            x = -a * b;
            y = a * -b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block(["
        "ExprStmt(Assign(Id(x), BinaryOp('*', UnaryOp('-', Id(a)), Id(b)))), "
        "ExprStmt(Assign(Id(y), BinaryOp('*', Id(a), UnaryOp('-', Id(b)))))]))])",
    )


def test_375():
    # Modulo combined with addition (precedence check)
    check_ast(
        r"""
        fn main() {
            x = a + b % c;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('+', Id(a), BinaryOp('%', Id(b), Id(c)))))]))])",
    )


def test_376():
    # Division and subtraction mix, left to right within each precedence level
    check_ast(
        r"""
        fn main() {
            x = a / b - c / d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('-', BinaryOp('/', Id(a), Id(b)), BinaryOp('/', Id(c), Id(d)))))]))])",
    )


def test_377():
    # Equality with a call and a field access as operands
    check_ast(
        r"""
        fn main() {
            x = get() == p.value;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('==', CallExpr(Id(get), []), FieldAccess(Id(p), Id(value)))))]))])",
    )


def test_378():
    # Assignment right-hand side is a full logical expression
    check_ast(
        r"""
        fn main() {
            ok = a < b && b < c;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(ok), "
        "BinaryOp('&&', BinaryOp('<', Id(a), Id(b)), BinaryOp('<', Id(b), Id(c)))))]))])",
    )


def test_379():
    # Not applied to a parenthesized relational expression
    check_ast(
        r"""
        fn main() {
            x = !(a == b);
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "UnaryOp('!', BinaryOp('==', Id(a), Id(b)))))]))])",
    )


def test_380():
    # Assignment to an array cell, right-hand side uses full precedence ladder
    check_ast(
        r"""
        fn main() {
            arr[0] = a + b * c - d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign("
        "ArrayCell(Id(arr), IntLiteral(0)), BinaryOp('-', BinaryOp('+', Id(a), "
        "BinaryOp('*', Id(b), Id(c))), Id(d))))]))])",
    )


def test_381():
    # Large mixed-precedence expression exercising every level at once
    check_ast(
        r"""
        fn main() {
            r = a + b * c > d - e / f && !g || h == i;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(r), "
        "BinaryOp('||', BinaryOp('&&', BinaryOp('>', BinaryOp('+', Id(a), "
        "BinaryOp('*', Id(b), Id(c))), BinaryOp('-', Id(d), BinaryOp('/', Id(e), Id(f)))), "
        "UnaryOp('!', Id(g))), BinaryOp('==', Id(h), Id(i)))))]))])",
    )


# =============================================================================
# Group 8: Nested Complex Accesses (test_381 - test_395)
# =============================================================================
def test_382():
    # Array index expression is itself a nested array access
    check_ast(
        r"""
        fn main() {
            x = arr[matrix[0][0]];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "ArrayCell(Id(arr), ArrayCell(ArrayCell(Id(matrix), IntLiteral(0)), "
        "IntLiteral(0)))))]))])",
    )


def test_383():
    # Call result indexed then field-accessed: func(a)[0].b
    check_ast(
        r"""
        fn main() {
            x = func(a)[0].b;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "FieldAccess(ArrayCell(CallExpr(Id(func), [Id(a)]), IntLiteral(0)), Id(b))))]))])",
    )


def test_384():
    # Deep chained field access
    check_ast(
        r"""
        fn main() {
            x = a.b.c.d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "FieldAccess(FieldAccess(FieldAccess(Id(a), Id(b)), Id(c)), Id(d))))]))])",
    )


def test_385():
    # Deep chained array indexing
    check_ast(
        r"""
        fn main() {
            x = a[0][1][2];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "ArrayCell(ArrayCell(ArrayCell(Id(a), IntLiteral(0)), IntLiteral(1)), "
        "IntLiteral(2))))]))])",
    )


def test_386():
    # Alternating index/field boundaries: arr -> field -> index -> field
    check_ast(
        r"""
        fn main() {
            x = data[i].values[j].total;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "FieldAccess(ArrayCell(FieldAccess(ArrayCell(Id(data), Id(i)), Id(values)), "
        "Id(j)), Id(total))))]))])",
    )


def test_387():
    # Triple nested function calls
    check_ast(
        r"""
        fn main() {
            x = f(g(h(x)));
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "CallExpr(Id(f), [CallExpr(Id(g), [CallExpr(Id(h), [Id(x)])])])))]))])",
    )


def test_388():
    # Array index expression containing a function call
    check_ast(
        r"""
        fn main() {
            x = arr[f(i) + 1];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "ArrayCell(Id(arr), BinaryOp('+', CallExpr(Id(f), [Id(i)]), IntLiteral(1)))))]))])",
    )


def test_389():
    # Two deep chains combined by an arithmetic operator
    check_ast(
        r"""
        fn main() {
            x = points[i].pos.x + points[j].pos.y;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "BinaryOp('+', FieldAccess(FieldAccess(ArrayCell(Id(points), Id(i)), Id(pos)), Id(x)), "
        "FieldAccess(FieldAccess(ArrayCell(Id(points), Id(j)), Id(pos)), Id(y)))))]))])",
    )


def test_390():
    # Index expression is itself a field access on both sides
    check_ast(
        r"""
        fn main() {
            x = a.b[c.d];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "ArrayCell(FieldAccess(Id(a), Id(b)), FieldAccess(Id(c), Id(d)))))]))])",
    )


def test_391():
    # Swapped nested array-index assignment (matrix transpose-style)
    check_ast(
        r"""
        fn main() {
            matrix[i][j] = matrix[j][i];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign("
        "ArrayCell(ArrayCell(Id(matrix), Id(i)), Id(j)), "
        "ArrayCell(ArrayCell(Id(matrix), Id(j)), Id(i))))]))])",
    )


def test_392():
    # Assignment between two field-then-index chains
    check_ast(
        r"""
        fn main() {
            obj.list[0] = obj.list[1];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign("
        "ArrayCell(FieldAccess(Id(obj), Id(list)), IntLiteral(0)), "
        "ArrayCell(FieldAccess(Id(obj), Id(list)), IntLiteral(1))))]))])",
    )


def test_393():
    # Parenthesized expression as the base of an index access
    check_ast(
        r"""
        fn main() {
            x = (a + b)[0];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "ArrayCell(BinaryOp('+', Id(a), Id(b)), IntLiteral(0))))]))])",
    )


def test_394():
    # Nested access boundary: index -> field -> index -> field
    check_ast(
        r"""
        fn main() {
            x = grid[i].cells[j].value;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "FieldAccess(ArrayCell(FieldAccess(ArrayCell(Id(grid), Id(i)), Id(cells)), Id(j)), "
        "Id(value))))]))])",
    )


def test_395():
    # Arithmetic precedence still applies inside a nested index expression
    check_ast(
        r"""
        fn main() {
            x = arr[i + j * k];
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "ArrayCell(Id(arr), BinaryOp('+', Id(i), BinaryOp('*', Id(j), Id(k))))))]))])",
    )


def test_396():
    # Field-field-index-field boundary chain
    check_ast(
        r"""
        fn main() {
            x = p.a.b[0].c;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(x), "
        "FieldAccess(ArrayCell(FieldAccess(FieldAccess(Id(p), Id(a)), Id(b)), IntLiteral(0)), "
        "Id(c))))]))])",
    )


# =============================================================================
# Group 9: Chained Assignment Expressions (test_396 - test_399)
# =============================================================================
def test_397():
    # Assignment expression used inside an if-condition
    check_ast(
        r"""
        fn main() {
            if (x = compute()) > 0 {
                y = 1;
            }
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([If("
        "BinaryOp('>', Assign(Id(x), CallExpr(Id(compute), [])), IntLiteral(0)), "
        "Block([ExprStmt(Assign(Id(y), IntLiteral(1)))]), None)]))])",
    )


def test_398():
    # Chained assignment where every target is a field access
    check_ast(
        r"""
        fn main() {
            a.b = c.d = e.f;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign("
        "FieldAccess(Id(a), Id(b)), Assign(FieldAccess(Id(c), Id(d)), "
        "FieldAccess(Id(e), Id(f)))))]))])",
    )


def test_399():
    # Chained assignment of three array-cell targets
    check_ast(
        r"""
        fn main() {
            x[0] = y[0] = z[0] = 1;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign("
        "ArrayCell(Id(x), IntLiteral(0)), Assign(ArrayCell(Id(y), IntLiteral(0)), "
        "Assign(ArrayCell(Id(z), IntLiteral(0)), IntLiteral(1)))))]))])",
    )


def test_400():
    # Chained assignment whose final right-hand side is a relational expression
    check_ast(
        r"""
        fn main() {
            a = b = c > d;
        }
        """,
        "Program([FuncDecl(Id(main), [], VoidType, Block([ExprStmt(Assign(Id(a), "
        "Assign(Id(b), BinaryOp('>', Id(c), Id(d)))))]))])",
    )
