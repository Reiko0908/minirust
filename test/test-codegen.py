import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"src"))

from TestUtils import CodeGenerator
from utils.AST import *

def check_codegen(ast_or_source, expected):
    result = CodeGenerator().generate_and_run(ast_or_source)
    assert result == expected, (
        f"Expected {expected!r}, got {result!r}"
    )

# ---------------------------------------------------------------------------
# 501-510: Basic statements, printing, variables, and functions
# ---------------------------------------------------------------------------
def test_501():
    check_codegen(
        "fn main() { print_i32(40000); print_i32(-40000); }",
        "40000-40000",
    )


def test_502():
    ast = Program([
        FuncDecl(
            "main",
            [],
            VoidType(),
            Block([
                ExprStmt(CallExpr("print_i32", [IntLiteral(2)])),
            ]),
        ),
    ])
    check_codegen(ast, "2")


def test_503():
    source = """
    fn main() {
        print_i32(-7);
        print_string("|");
        print_f32(1.5);
        print_string("|");
        print_bool(true);
        print_string("|ok");
    }
    """
    check_codegen(source, "-7|1.5|true|ok")


def test_504():
    check_codegen("fn main() { print_i32(2 + 3 * 4); }", "14")


def test_505():
    check_codegen("fn main() { let x = 42; println_i32(x); }", "42\n")


def test_506():
    source = """
    fn add(a: i32, b: i32) -> i32 { return a + b; }
    fn main() { print_i32(add(8, 9)); }
    """
    check_codegen(source, "17")


def test_507():
    source = """
    fn main() { print_i32(later(5)); }
    fn later(x: i32) -> i32 { return x * 2; }
    """
    check_codegen(source, "10")


def test_508():
    source = """
    fn mark(x: i32) -> i32 {
        print_i32(x);
        return x;
    }

    fn mix(a: i32, b: i32, c: i32) -> i32 {
        return a + b * c;
    }

    fn main() {
        mix(mark(1), mark(2), mark(3));
        print_i32(mix(2, 3, 4));
    }
    """
    check_codegen(source, "12314")


def test_509():
    check_codegen(r'fn main() { print_string("\"\\"); }', '"\\')


def test_510():
    source = """
    fn main() {
        println_f32(1.5);
        println_bool(false);
        println_string("ok");
        println();
    }
    """
    check_codegen(source, "1.5\nfalse\nok\n\n")


# ---------------------------------------------------------------------------
# 511-515: Basic switch control flow
# ---------------------------------------------------------------------------
def test_511():
    source = """
    fn main() {
        switch 2 {
            case 1: print_string("a"); break;
            case 2: print_string("b"); break;
            default: print_string("d");
        }
    }
    """
    check_codegen(source, "b")


def test_512():
    source = """
    fn main() {
        switch 9 {
            case 1: print_string("a"); break;
            default: print_string("d");
        }
    }
    """
    check_codegen(source, "d")


def test_513():
    source = """
    fn main() {
        switch 1 {
            case 1: print_string("a");
            case 2: print_string("b");
            default: print_string("d");
        }
    }
    """
    check_codegen(source, "abd")


def test_514():
    source = """
    fn main() {
        switch 1 {
            case 1: print_string("a"); break;
            case 2: print_string("b");
            default: print_string("d");
        }
    }
    """
    check_codegen(source, "a")


def test_515():
    source = """
    fn main() {
        switch true {
            case false: print_i32(0); break;
            case true: print_i32(1); break;
        }
    }
    """
    check_codegen(source, "1")


# ---------------------------------------------------------------------------
# 516-525: While and for loops
# ---------------------------------------------------------------------------
def test_516():
    source = """
    fn main() {
        let mut i = 0;
        while i < 3 {
            print_i32(i);
            i = i + 1;
        }
    }
    """
    check_codegen(source, "012")


def test_517():
    check_codegen("fn main() { while false { print_i32(1); } print_i32(2); }", "2")


def test_518():
    check_codegen("fn main() { for i in 0..5 { print_i32(i); } }", "01234")


def test_519():
    check_codegen("fn main() { for i in 3..6 { print_i32(i); } }", "345")


def test_520():
    check_codegen("fn main() { for i in 0..1 { print_i32(i); } }", "0")


def test_521():
    source = """
    fn main() {
        let mut i = 0;
        while i < 2 {
            let mut j = 0;
            while j < 2 {
                print_i32(i * 2 + j);
                j = j + 1;
            }
            i = i + 1;
        }
    }
    """
    check_codegen(source, "0123")


def test_522():
    source = """
    fn main() {
        for i in 1..3 {
            for j in 1..3 {
                print_i32(i * 10 + j);
            }
        }
    }
    """
    check_codegen(source, "11122122")


def test_523():
    source = """
    fn start_value() -> i32 {
        print_string("s");
        return 0;
    }
    fn end_value() -> i32 {
        print_string("e");
        return 3;
    }
    fn main() {
        for i in start_value()..end_value() {
            print_i32(i);
        }
    }
    """
    check_codegen(source, "se0e1e2e")


def test_524():
    source = """
    fn main() {
        let start = 2;
        let end = 5;
        for i in start..end { println_i32(i); }
    }
    """
    check_codegen(source, "2\n3\n4\n")


def test_525():
    check_codegen("fn main() { for i in 4..4 { print_i32(i); } print_i32(7); }", "7")


# ---------------------------------------------------------------------------
# 526-534: Break and continue
# ---------------------------------------------------------------------------
def test_526():
    source = """
    fn main() {
        let mut i = 0;
        while true {
            if i == 3 { break; }
            print_i32(i);
            i = i + 1;
        }
    }
    """
    check_codegen(source, "012")


def test_527():
    source = """
    fn main() {
        let mut i = 0;
        while i < 5 {
            i = i + 1;
            if i % 2 == 0 { continue; }
            print_i32(i);
        }
    }
    """
    check_codegen(source, "135")


def test_528():
    check_codegen("fn main() { for i in 0..9 { if i == 3 { break; } print_i32(i); } }", "012")


def test_529():
    check_codegen("fn main() { for i in 0..6 { if i % 2 == 0 { continue; } print_i32(i); } }", "135")


def test_530():
    source = """
    fn main() {
        for i in 0..3 {
            for j in 0..3 {
                if j == 1 { break; }
                print_i32(i);
            }
        }
    }
    """
    check_codegen(source, "012")


def test_531():
    source = """
    fn main() {
        for i in 0..2 {
            for j in 0..3 {
                if j == 1 { continue; }
                print_i32(i * 10 + j);
            }
        }
    }
    """
    check_codegen(source, "021012")


def test_532():
    source = """
    fn main() {
        for i in 0..2 {
            switch i {
                case 0: print_string("a"); break;
                default: print_string("b");
            }
        }
    }
    """
    check_codegen(source, "ab")


def test_533():
    source = """
    fn main() {
        for i in 0..4 {
            switch i {
                case 1: continue;
                case 3: continue;
                default: print_i32(i); break;
            }
        }
    }
    """
    check_codegen(source, "02")


def test_534():
    source = """
    fn main() {
        let mut i = 0;
        while i < 2 {
            switch i {
                case 0: print_string("s"); break;
                default: print_string("t");
            }
            print_string("l");
            i = i + 1;
        }
    }
    """
    check_codegen(source, "sltl")


# ---------------------------------------------------------------------------
# 535-540: Loop boundaries and loop-variable behavior
# ---------------------------------------------------------------------------
def test_535():
    check_codegen("fn main() { for i in -2..1 { print_i32(i); } }", "-2-10")


def test_536():
    check_codegen("fn main() { for i in 1 + 1..2 * 3 { print_i32(i); } }", "2345")


def test_537():
    source = """
    fn main() {
        let a = 2;
        let b = 4;
        for i in a..b { print_i32(i); }
    }
    """
    check_codegen(source, "23")


def test_538():
    source = """
    fn main() {
        let mut x = 3;
        while x > 0 {
            print_i32(x);
            x = x - 1;
        }
    }
    """
    check_codegen(source, "321")


def test_539():
    source = """
    fn main() {
        for i in 0..2 {
            for j in i..2 { print_i32(i * 10 + j); }
        }
    }
    """
    check_codegen(source, "0111")


def test_540():
    check_codegen("fn main() { for i in 5..3 { print_i32(i); } print_string(\"ok\"); }", "ok")


# ---------------------------------------------------------------------------
# 541-545: Advanced switch behavior
# ---------------------------------------------------------------------------
def test_541():
    source = """
    fn main() {
        switch 2 {
            case 1: print_i32(1);
            case 2: print_i32(2);
            case 3: print_i32(3);
        }
    }
    """
    check_codegen(source, "23")


def test_542():
    ast = Program([
        FuncDecl(
            Id("main"),
            [],
            VoidType(),
            Block([
                Switch(
                    IntLiteral(1),
                    [
                        Case(None, [
                            ExprStmt(CallExpr(Id("print_string"), [StringLiteral("d")])),
                        ]),
                        Case(IntLiteral(1), [
                            ExprStmt(CallExpr(Id("print_i32"), [IntLiteral(1)])),
                        ]),
                    ],
                ),
            ]),
        ),
    ])
    check_codegen(ast, "1")


def test_543():
    source = """
    fn choose() -> i32 {
        print_string("x");
        return 2;
    }

    fn main() {
        switch choose() {
            case 2: print_i32(2); break;
            default: print_i32(0);
        }
    }
    """
    check_codegen(source, "x2")


def test_544():
    source = """
    fn main() {
        switch 1 {
            case 1: let x = 7;
            case 2: print_i32(x); break;
        }
    }
    """
    check_codegen(source, "7")


def test_545():
    source = """
    fn main() {
        switch 1 {
            case 1:
                switch 2 {
                    case 2: print_string("a"); break;
                }
                print_string("b");
                break;
        }
    }
    """
    check_codegen(source, "ab")


# ---------------------------------------------------------------------------
# 546-552: Struct lifecycle and field access
# ---------------------------------------------------------------------------
def test_546():
    source = """
    struct P { x: i32 }
    fn main() {
        let p = P { x: 5 };
        print_i32(p.x);
    }
    """
    check_codegen(source, "5")


def test_547():
    box = StructDecl(
        "Box",
        [VarDecl("value", FloatType())],
    )
    init = StructInit(
        "Box",
        [FieldInit("value", IntLiteral(2))],
    )
    main = FuncDecl(
        "main",
        [],
        VoidType(),
        Block([
            VarDecl("b", StructType("Box"), init, False),
            ExprStmt(
                CallExpr(
                    "print_f32",
                    [FieldAccess(Id("b"), "value")],
                )
            ),
        ]),
    )
    check_codegen(Program([box, main]), "2.0")


def test_548():
    source = """
    struct P { x: i32 }
    fn main() {
        let mut p = P { x: 1 };
        p.x = 9;
        print_i32(p.x);
    }
    """
    check_codegen(source, "9")


def test_549():
    source = """
    struct Inner { x: i32 }
    struct Outer { inner: Inner }
    fn main() {
        let o = Outer { inner: Inner { x: 8 } };
        print_i32(o.inner.x);
    }
    """
    check_codegen(source, "8")


def test_550():
    source = """
    struct P { x: i32 }
    fn show(items: [P; 2]) { print_i32(items[1].x); }
    fn main() { show([P { x: 5 }, P { x: 6 }]); }
    """
    check_codegen(source, "6")


def test_551():
    source = """
    struct P { x: i32 }
    fn make(x: i32) -> P { return P { x: x }; }
    fn main() { print_i32(make(11).x); }
    """
    check_codegen(source, "11")


def test_552():
    source = """
    struct Bag { values: [string; 3] }
    fn main() {
        let mut b = Bag { values: ["a", "b", "c"] };
        b.values[1] = "z";
        print_string(b.values[0]);
        print_string(b.values[1]);
        print_string(b.values[2]);
    }
    """
    check_codegen(source, "azc")


# ---------------------------------------------------------------------------
# 553-557: Short-circuit logical operations
# ---------------------------------------------------------------------------
def test_553():
    check_codegen("fn main() { print_bool(false && (1 / 0 > 0)); }", "false")


def test_554():
    check_codegen("fn main() { print_bool(true || (1 / 0 > 0)); }", "true")


def test_555():
    source = """
    fn mark(x: i32) -> bool {
        print_i32(x);
        return true;
    }

    fn main() {
        true && mark(2);
    }
    """
    check_codegen(source, "2")


def test_556():
    source = """
    fn mark(x: i32) -> bool {
        print_i32(x);
        return true;
    }

    fn main() {
        false || mark(3);
    }
    """
    check_codegen(source, "3")


def test_557():
    source = """
    fn mark(x: i32) -> bool {
        print_i32(x);
        return true;
    }

    fn main() {
        false && mark(1);
        true || mark(2);
    }
    """
    check_codegen(source, "")


# ---------------------------------------------------------------------------
# 558-567: Nested loop-control scenarios
# ---------------------------------------------------------------------------
def test_558():
    source = """
    fn main() {
        let mut x = 0;
        while true {
            x = x + 1;
            if x == 2 { break; }
        }
        print_i32(x);
    }
    """
    check_codegen(source, "2")


def test_559():
    check_codegen("fn main() { for i in 0..4 { if i < 3 { continue; } print_i32(i); } }", "3")


def test_560():
    source = """
    fn main() {
        for i in 0..3 {
            let mut j = 0;
            while true {
                print_i32(i);
                break;
            }
        }
    }
    """
    check_codegen(source, "012")


def test_561():
    source = """
    fn main() {
        let mut i = 0;
        while i < 3 {
            i = i + 1;
            switch i {
                case 2: continue;
                default: print_i32(i); break;
            }
        }
    }
    """
    check_codegen(source, "13")


def test_562():
    source = """
    fn main() {
        for i in 0..3 {
            switch i {
                case 1: break;
                default: print_i32(i); break;
            }
            print_string("x");
        }
    }
    """
    check_codegen(source, "0xx2x")


def test_563():
    source = """
    fn main() {
        for i in 0..3 {
            if i == 1 {
                { continue; }
            }
            print_i32(i);
        }
    }
    """
    check_codegen(source, "02")


def test_564():
    source = """
    fn main() {
        let mut i = 0;
        while true {
            while true { break; }
            i = i + 1;
            if i == 2 { break; }
        }
        print_i32(i);
    }
    """
    check_codegen(source, "2")


def test_565():
    source = """
    fn main() {
        for i in 0..2 {
            for j in 0..3 {
                if j == 2 { continue; }
                print_i32(i + j);
            }
        }
    }
    """
    check_codegen(source, "0112")


def test_566():
    source = """
    fn main() {
        let mut i = 0;
        while i < 4 {
            i = i + 1;
            if i == 2 { continue; }
            if i == 4 { break; }
            print_i32(i);
        }
    }
    """
    check_codegen(source, "13")


def test_567():
    source = """
    fn main() {
        for i in 0..3 {
            switch i {
                case 0: continue;
                case 1: print_i32(1); break;
                default: break;
            }
            print_i32(9);
        }
    }
    """
    check_codegen(source, "199")


# ---------------------------------------------------------------------------
# 568-575: Assignment expressions and lvalues
# ---------------------------------------------------------------------------
def test_568():
    check_codegen("fn main() { let mut x = 0; x = 8; print_i32(x); }", "8")


def test_569():
    source = """
    fn main() {
        let mut a = 0;
        let mut b = 0;
        b = 7;
        a = b;
        print_i32(a);
        print_i32(b);
    }
    """
    check_codegen(source, "77")


def test_570():
    source = """
    fn main() {
        let mut a: f32 = 0.0;
        let mut b: f32 = 0.0;
        b = 2;
        a = b;
        print_f32(a);
        print_string("|");
        print_f32(b);
    }
    """
    check_codegen(source, "2.0|2.0")


def test_571():
    source = """
    fn main() {
        let mut flag = false;
        flag = true;
        if flag { print_bool(flag); }
    }
    """
    check_codegen(source, "true")


def test_572():
    source = """
    fn main() {
        let mut a = [true, false, false];
        a[1] = true;
        print_bool(a[0]);
        print_bool(a[1]);
        print_bool(a[2]);
    }
    """
    check_codegen(source, "truetruefalse")


def test_573():
    source = """
    struct P { x: i32 }
    fn main() {
        let mut p = P { x: 0 };
        p.x = 12;
        print_i32(p.x);
    }
    """
    check_codegen(source, "12")


def test_574():
    source = """
    fn main() {
        let mut a = [[1, 2], [3, 4]];
        a[1][0] = 9;
        print_i32(a[1][0]);
    }
    """
    check_codegen(source, "9")


def test_575():
    source = """
    fn set() {
        let mut x = 0;
        return x = 13;
    }
    fn main() {
        set();
        print_string("ok");
    }
    """
    check_codegen(source, "ok")


# ---------------------------------------------------------------------------
# 576-580: Relational and logical behavior
# ---------------------------------------------------------------------------
def test_576():
    check_codegen("fn main() { print_bool(2 < 3); }", "true")


def test_577():
    main = FuncDecl(
        "main",
        [],
        VoidType(),
        Block([
            ExprStmt(
                CallExpr(
                    "print_bool",
                    [
                        BinaryOp(
                            "<",
                            FloatLiteral(1.5),
                            FloatLiteral(2.5),
                        )
                    ],
                )
            ),
            ExprStmt(
                CallExpr(
                    "print_bool",
                    [
                        BinaryOp(
                            ">=",
                            FloatLiteral(2.5),
                            IntLiteral(2),
                        )
                    ],
                )
            ),
            ExprStmt(
                CallExpr(
                    "print_bool",
                    [
                        BinaryOp(
                            "!=",
                            IntLiteral(2),
                            FloatLiteral(3.0),
                        )
                    ],
                )
            ),
        ]),
    )
    check_codegen(Program([main]), "truetruetrue")


def test_578():
    source = """
    fn main() {
        print_bool(2 == 2);
        print_bool(2 != 3);
        print_bool(3 >= 3);
        print_bool(2 <= 1);
    }
    """
    check_codegen(source, "truetruetruefalse")


def test_579():
    source = """
    fn main() {
        let x = 4;
        if x > 0 && x < 5 { print_string("yes"); }
        else { print_string("no"); }
    }
    """
    check_codegen(source, "yes")


def test_580():
    check_codegen(
        "fn main() { print_bool(!(1 > 2) && 3 == 3); }",
        "true",
    )


# ---------------------------------------------------------------------------
# 581-585: Unary operations
# ---------------------------------------------------------------------------
def test_581():
    check_codegen("fn main() { print_i32(-5); }", "-5")


def test_582():
    check_codegen("fn main() { print_f32(-2.5); }", "-2.5")


def test_583():
    check_codegen("fn main() { print_bool(!true); }", "false")


def test_584():
    check_codegen("fn main() { print_bool(!!false); }", "false")


def test_585():
    check_codegen("fn main() { print_i32(-(-3 + 1)); }", "2")


# ---------------------------------------------------------------------------
# 586-590: Floating point and coercion
# ---------------------------------------------------------------------------
def test_586():
    check_codegen("fn main() { print_f32(1 + 2.5); }", "3.5")


def test_587():
    source = """
    fn main() {
        let mut x: f32 = 0.0;
        x = 3;
        print_f32(x);
    }
    """
    check_codegen(source, "3.0")


def test_588():
    source = """
    fn main() {
        let x: f32 = 3;
        let values: [f32; 2] = [4.0, 5.0];
        print_f32(x);
        print_f32(values[0]);
        print_f32(values[1]);
    }
    """
    check_codegen(source, "3.04.05.0")


def test_589():
    twice = FuncDecl(
        "twice",
        [VarDecl("x", FloatType())],
        FloatType(),
        Block([
            Return(
                BinaryOp(
                    "*",
                    Id("x"),
                    FloatLiteral(2.0),
                )
            ),
        ]),
    )
    main = FuncDecl(
        "main",
        [],
        VoidType(),
        Block([
            ExprStmt(
                CallExpr(
                    "print_f32",
                    [CallExpr("twice", [IntLiteral(3)])],
                )
            ),
        ]),
    )
    check_codegen(Program([twice, main]), "6.0")


def test_590():
    to_float = FuncDecl(
        "to_float",
        [],
        FloatType(),
        Block([Return(IntLiteral(5))]),
    )
    main = FuncDecl(
        "main",
        [],
        VoidType(),
        Block([
            ExprStmt(
                CallExpr(
                    "print_f32",
                    [CallExpr("to_float", [])],
                )
            ),
        ]),
    )
    check_codegen(Program([to_float, main]), "5.0")


# ---------------------------------------------------------------------------
# 591-598: Recursion and scope
# ---------------------------------------------------------------------------
def test_591():
    source = """
    fn fact(n: i32) -> i32 {
        if n <= 1 { return 1; }
        return n * fact(n - 1);
    }
    fn main() { print_i32(fact(5)); }
    """
    check_codegen(source, "120")


def test_592():
    source = """
    fn fib(n: i32) -> i32 {
        if n <= 1 { return n; }
        return fib(n - 1) + fib(n - 2);
    }
    fn main() { print_i32(fib(8)); }
    """
    check_codegen(source, "21")


def test_593():
    source = """
    fn even(n: i32) -> bool {
        if n == 0 { return true; }
        return odd(n - 1);
    }
    fn odd(n: i32) -> bool {
        if n == 0 { return false; }
        return even(n - 1);
    }
    fn main() {
        print_bool(even(8));
        print_bool(odd(7));
    }
    """
    check_codegen(source, "truetrue")


def test_594():
    source = """
    fn main() {
        let x = 1;
        {
            let x = 2;
            print_i32(x);
        }
        print_i32(x);
    }
    """
    check_codegen(source, "21")


def test_595():
    source = """
    fn main() {
        for i in 1..16 {
            if i % 15 == 0 { print_string("FizzBuzz"); continue; }
            if i % 3 == 0 { print_string("Fizz"); continue; }
            if i % 5 == 0 { print_string("Buzz"); continue; }
            print_i32(i);
            print_string(",");
        }
    }
    """
    check_codegen(source, "1,2,Fizz4,BuzzFizz7,8,FizzBuzz11,Fizz13,14,FizzBuzz")


def test_596():
    source = """
    fn sum(n: i32) -> i32 {
        if n == 0 { return 0; }
        return n + sum(n - 1);
    }
    fn main() { print_i32(sum(10)); }
    """
    check_codegen(source, "55")


def test_597():
    source = """
    fn first(x: i32) -> i32 { return second(x) + 1; }
    fn main() { print_i32(first(5)); }
    fn second(x: i32) -> i32 { return x * 2; }
    """
    check_codegen(source, "11")


def test_598():
    source = """
    fn make() -> [i32; 2] {
        return [3, 4];
    }

    fn first(values: [i32; 2]) -> i32 {
        return values[0];
    }

    fn main() {
        print_i32(first(make()));
    }
    """
    check_codegen(source, "3")


# ---------------------------------------------------------------------------
# 599-600: Struct parameters and integrated program
# ---------------------------------------------------------------------------
def test_599():
    source = """
    struct Pair { a: i32, b: i32 }
    fn total(p: Pair) -> i32 { return p.a + p.b; }
    fn main() { print_i32(total(Pair { a: 20, b: 22 })); }
    """
    check_codegen(source, "42")


def test_600():
    source = """
    struct Counter { value: i32 }
    fn step(c: Counter, amount: i32) -> Counter {
        let mut result = Counter { value: c.value };
        result.value = result.value + amount;
        return result;
    }
    fn main() {
        let mut c = Counter { value: 0 };
        for i in 1..6 {
            if i == 3 { continue; }
            c = step(c, i);
        }
        switch c.value {
            case 12: print_string("ok:");
            default: print_i32(c.value);
        }
    }
    """
    check_codegen(source, "ok:12")
