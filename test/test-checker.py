import pytest
from checker.StaticChecker import StaticChecker
from checker.StaticError import *
from TestUtils import TestChecker
from utils.AST import *


# ---- Scope Errors (test_401 - test_420) ----

def test_401():
    # duplicate local variable in same block
    source = "fn main() { let x = 1; let x = 2; }"
    TestChecker.checkChecker(source, "Redeclared(Variable, x)")

def test_402():
    # duplicate function declaration
    source = "fn foo() {} fn foo() {} fn main() {}"
    TestChecker.checkChecker(source, "Redeclared(Function, foo)")

def test_403():
    # duplicate struct declaration
    source = "struct Point { x: i32 } struct Point { y: i32 } fn main() {}"
    TestChecker.checkChecker(source, "Redeclared(Struct, Point)")

def test_404():
    # duplicate parameter name
    source = "fn f(a: i32, a: i32) -> i32 { return a; } fn main() {}"
    TestChecker.checkChecker(source, "Redeclared(Parameter, a)")

def test_405():
    # nested block variable shadows a parameter
    source = "fn f(a: i32) { { let a = 1; } } fn main() {}"
    TestChecker.checkChecker(source, "Redeclared(Variable, a)")

def test_406():
    # duplicate struct field name
    source = "struct P { x: i32, x: i32 } fn main() {}"
    TestChecker.checkChecker(source, "Redeclared(Member, x)")

def test_407():
    # undeclared identifier used in a call
    source = "fn main() { println_i32(y); }"
    TestChecker.checkChecker(source, "UndeclaredIdentifier(y)")

def test_408():
    # undeclared struct type used in a var decl
    source = "fn main() { let p: Foo = 1; }"
    TestChecker.checkChecker(source, "UndeclaredStruct(Foo)")

def test_409():
    # undeclared struct type used as a parameter type
    source = "fn f(p: Foo) {} fn main() {}"
    TestChecker.checkChecker(source, "UndeclaredStruct(Foo)")

def test_410():
    # undeclared struct type used as a struct field type
    source = "struct Bar { inner: Missing } fn main() {}"
    TestChecker.checkChecker(source, "UndeclaredStruct(Missing)")

def test_411():
    # shadowing across different nested blocks is legal
    source = "fn main() { let x = 1; { let x = 2; } }"
    TestChecker.checkChecker(source, "Success")

def test_412():
    # mutual recursion between functions declared in reverse call order
    source = "fn a() { b(); } fn b() { a(); } fn main() {}"
    TestChecker.checkChecker(source, "Success")

def test_413():
    # struct field referencing a struct declared later in the file
    source = "struct A { b: B } struct B { v: i32 } fn main() {}"
    TestChecker.checkChecker(source, "Success")

def test_414():
    # variable from one block is not visible in a sibling block
    source = "fn main() { { let x = 1; } println_i32(x); }"
    TestChecker.checkChecker(source, "UndeclaredIdentifier(x)")

def test_415():
    # same variable name reused across two different functions
    source = "fn f() { let x = 1; } fn g() { let x = 2; } fn main() {}"
    TestChecker.checkChecker(source, "Success")

def test_416():
    # re-declaring a name after its earlier block has ended
    source = "fn main() { { let x = 1; } let x = 2; }"
    TestChecker.checkChecker(source, "Success")

def test_417():
    # redeclaring a function with a different signature still conflicts
    source = "fn foo(a: i32) {} fn foo() {} fn main() {}"
    TestChecker.checkChecker(source, "Redeclared(Function, foo)")

def test_418():
    # a struct and a function may share the same name (separate namespaces)
    source = "struct Point { x: i32 } fn Point() {} fn main() {}"
    TestChecker.checkChecker(source, "Success")

def test_419():
    # nested and sibling blocks may shadow an outer local independently
    source = """
fn main() {
    let x = 0;
    {
        let x = 1;
        { let y = x + 1; println_i32(y); }
    }
    { let x = 2; println_i32(x); }
    println_i32(x);
}
"""
    TestChecker.checkChecker(source, "Success")

def test_420():
    # call to an undeclared function from inside a nested block
    source = "fn main() { { foo(); } }"
    TestChecker.checkChecker(source, "UndeclaredFunction(foo)")

# ---- Type Mismatch Errors (test_421 - test_435) ----

def test_421():
    # adding i32 and bool
    source = "fn main() { let x = 1 + true; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(BinaryOp('+', IntLiteral(1), BoolLiteral(True)))")

def test_422():
    # mixed int/float array literal infers f32 regardless of which order the int and float elements appear in
    source = "fn main() { let x = [1, 2.0]; let y = [2.0, 1]; }"
    TestChecker.checkChecker(source, "Success")

def test_423():
    # modulo requires both operands to be i32
    source = "fn main() { let x = 5.0 % 2.0; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(BinaryOp('%', FloatLiteral(5.0), FloatLiteral(2.0)))")

def test_424():
    # equality is numeric-only, string == string is illegal
    source = "fn main() { let x = \"a\" == \"b\"; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(BinaryOp('==', StringLiteral(\"a\"), StringLiteral(\"b\")))")

def test_425():
    # logical AND requires bool operands
    source = "fn main() { let x = 1 && true; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(BinaryOp('&&', IntLiteral(1), BoolLiteral(True)))")

def test_426():
    # if condition must be bool
    source = "fn main() { if 1 { } }"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(If(IntLiteral(1), Block([]), None))")

def test_427():
    # while condition must be bool
    source = "fn main() { while 1 { } }"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(While(IntLiteral(1), Block([])))")

def test_428():
    # for loop bounds must be i32
    source = "fn main() { for i in 0..true { } }"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(For(Id(i), IntLiteral(0), BoolLiteral(True), Block([])))")

def test_429():
    # var decl explicit bool type but i32 initializer
    source = "fn main() { let x: bool = 1; }"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(VarDecl(Id(x), BoolType, IntLiteral(1), False))")

def test_430():
    # var decl explicit f32 type with i32 initializer is legal (coercion)
    source = "fn main() { let x: f32 = 1; }"
    TestChecker.checkChecker(source, "Success")

def test_431():
    # function declared to return i32 but returns a bool
    source = "fn f() -> i32 { return true; } fn main() {}"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(Return(BoolLiteral(True)))")

def test_432():
    # returning a value from a void function
    source = "fn f() { return 1; } fn main() {}"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(Return(IntLiteral(1)))")

def test_433():
    # returning nothing from a non-void function
    source = "fn f() -> i32 { return; } fn main() {}"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(Return(None))")

def test_434():
    # unary minus on a bool
    source = "fn main() { let x = -true; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(UnaryOp('-', BoolLiteral(True)))")

def test_435():
    # unary not on an i32
    source = "fn main() { let x = !1; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(UnaryOp('!', IntLiteral(1)))")

# ---- Assignment Errors (test_436 - test_445) ----

def test_436():
    # assigning to an immutable let-bound variable
    source = "fn main() { let x = 1; x = 2; }"
    TestChecker.checkChecker(source, "CannotAssignToConstant(Id(x))")

def test_437():
    # assigning to a function parameter
    source = "fn f(a: i32) { a = 2; } fn main() {}"
    TestChecker.checkChecker(source, "CannotAssignToConstant(Id(a))")

def test_438():
    # assigning to a mutable variable is legal
    source = "fn main() { let mut x = 1; x = 2; }"
    TestChecker.checkChecker(source, "Success")

def test_439():
    # assigning an array of the wrong size, even with a matching element type (no down-coercion, no size coercion)
    source = "fn main() { let a: [i32; 2] = [1, 2]; let mut b: [i32; 3] = [1, 2, 3]; b = a; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(Assign(Id(b), Id(a)))")

def test_440():
    # assigning an i32 value into an f32 variable is legal (coercion)
    source = "fn main() { let mut x: f32 = 1.0; x = 5; }"
    TestChecker.checkChecker(source, "Success")

def test_441():
    # assigning to a field of an immutable struct variable
    source = "struct P { x: i32 } fn main() { let p = P { x: 1 }; p.x = 2; }"
    TestChecker.checkChecker(source, "CannotAssignToConstant(FieldAccess(Id(p), Id(x)))")

def test_442():
    # assigning to a field of a mutable struct variable is legal
    source = "struct P { x: i32 } fn main() { let mut p = P { x: 1 }; p.x = 2; }"
    TestChecker.checkChecker(source, "Success")

def test_443():
    # assigning to an element of an immutable array
    source = "fn main() { let a: [i32; 2] = [1, 2]; a[0] = 3; }"
    TestChecker.checkChecker(source, "CannotAssignToConstant(ArrayCell(Id(a), IntLiteral(0)))")

def test_444():
    # assigning to an element of a mutable array is legal
    source = "fn main() { let mut a: [i32; 2] = [1, 2]; a[0] = 3; }"
    TestChecker.checkChecker(source, "Success")

def test_445():
    # assigning to a for-loop variable, which is implicitly immutable
    source = "fn main() { for i in 0..5 { i = 1; } }"
    TestChecker.checkChecker(source, "CannotAssignToConstant(Id(i))")

# ---- Struct Instantiation Errors (test_446 - test_457) ----

def test_446():
    # struct init missing a required field
    source = "struct P { x: i32, y: i32 } fn main() { let p = P { x: 1 }; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(StructInit(Id(P), [FieldInit(Id(x), IntLiteral(1))]))")

def test_447():
    # struct init with an unknown extra field
    source = "struct P { x: i32 } fn main() { let p = P { x: 1, y: 2 }; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(StructInit(Id(P), [FieldInit(Id(x), IntLiteral(1)), FieldInit(Id(y), IntLiteral(2))]))")

def test_448():
    # struct init field with the wrong type
    source = "struct P { x: i32 } fn main() { let p = P { x: true }; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(StructInit(Id(P), [FieldInit(Id(x), BoolLiteral(True))]))")

def test_449():
    # struct init referencing an undeclared struct name
    source = "fn main() { let p = Missing { x: 1 }; }"
    TestChecker.checkChecker(source, "UndeclaredStruct(Missing)")

def test_450():
    # struct init with all fields correctly provided
    source = "struct P { x: i32, y: i32 } fn main() { let p = P { x: 1, y: 2 }; }"
    TestChecker.checkChecker(source, "Success")

def test_451():
    # struct init field value coerces i32 into an f32 field
    source = "struct P { x: f32 } fn main() { let p = P { x: 1 }; }"
    TestChecker.checkChecker(source, "Success")

def test_452():
    # nested struct init: a struct field initialized with another struct
    source = "struct Inner { v: i32 } struct Outer { i: Inner } fn main() { let o = Outer { i: Inner { v: 1 } }; }"
    TestChecker.checkChecker(source, "Success")

def test_453():
    # struct init field expecting one struct type but given a different struct type with an identical field shape
    source = "struct A { v: i32 } struct B { v: i32 } struct Holder { inner: A } fn main() { let b = B { v: 1 }; let h = Holder { inner: b }; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(StructInit(Id(Holder), [FieldInit(Id(inner), Id(b))]))")

def test_454():
    # directly self-referencing struct is illegal
    source = "struct Node { next: Node } fn main() {}"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(VarDecl(Id(next), StructType(Id(Node)), None, False))")

def test_455():
    # indirectly (two-hop) recursive structs, with the offending field not being the struct's first field
    source = "struct A { x: i32, y: B } struct B { a: A } fn main() {}"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(VarDecl(Id(a), StructType(Id(A)), None, False))")

def test_456():
    # recursion through an array-of-struct field that is not the struct's first field
    source = "struct Node { label: i32, children: [Node; 4] } fn main() {}"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(VarDecl(Id(children), ArrayType(StructType(Id(Node)), 4), None, False))")

def test_457():
    # nested structs, arrays, field access, indexing, and a function call work together
    source = """
struct Point { x: i32 }
struct Pair { items: [Point; 2] }
fn sum(pair: Pair) -> i32 {
    return pair.items[0].x + pair.items[1].x;
}
fn main() {
    let pairs: [Pair; 2] = [
        Pair { items: [Point { x: 1 }, Point { x: 2 }] },
        Pair { items: [Point { x: 3 }, Point { x: 4 }] }
    ];
    println_i32(sum(pairs[1]));
}
"""
    TestChecker.checkChecker(source, "Success")

# ---- Field Access Errors (test_458 - test_465) ----

def test_458():
    # field access on a non-struct value
    source = "fn main() { let x = 1; let y = x.f; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(FieldAccess(Id(x), Id(f)))")

def test_459():
    # accessing a field that does not exist on the struct
    source = "struct P { x: i32 } fn main() { let p = P { x: 1 }; let y = p.z; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(FieldAccess(Id(p), Id(z)))")

def test_460():
    # accessing an existing field is legal
    source = "struct P { x: i32 } fn main() { let p = P { x: 1 }; let y = p.x; }"
    TestChecker.checkChecker(source, "Success")

def test_461():
    # chained field access through two struct levels is legal
    source = "struct Inner { v: i32 } struct Outer { i: Inner } fn main() { let o = Outer { i: Inner { v: 1 } }; let y = o.i.v; }"
    TestChecker.checkChecker(source, "Success")

def test_462():
    # chained field access fails at the second hop
    source = "struct Inner { v: i32 } struct Outer { i: Inner } fn main() { let o = Outer { i: Inner { v: 1 } }; let y = o.i.missing; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(FieldAccess(FieldAccess(Id(o), Id(i)), Id(missing)))")

def test_463():
    # field access on an undeclared identifier
    source = "fn main() { let y = missing.f; }"
    TestChecker.checkChecker(source, "UndeclaredIdentifier(missing)")

def test_464():
    # field access on an array element is legal
    source = "struct P { x: i32 } fn main() { let arr: [P; 1] = [P { x: 1 }]; let y = arr[0].x; }"
    TestChecker.checkChecker(source, "Success")

def test_465():
    # field access on the result of a function call is legal
    source = "struct P { x: i32 } fn make() -> P { return P { x: 1 }; } fn main() { let y = make().x; }"
    TestChecker.checkChecker(source, "Success")

# ---- Loop Control Errors (test_466 - test_470) ----

def test_466():
    # break used at top level, outside any loop or switch
    source = "fn main() { break; }"
    TestChecker.checkChecker(source, "MustInLoop(Break())")

def test_467():
    # continue used at top level, outside any loop
    source = "fn main() { continue; }"
    TestChecker.checkChecker(source, "MustInLoop(Continue())")

def test_468():
    # break inside a while loop is legal
    source = "fn main() { while true { break; } }"
    TestChecker.checkChecker(source, "Success")

def test_469():
    # break inside a switch with no enclosing loop is legal
    source = "fn main() { switch 1 { case 1: break; default: break; } }"
    TestChecker.checkChecker(source, "Success")

def test_470():
    # continue inside a switch with no enclosing loop is still illegal
    source = "fn main() { switch 1 { case 1: continue; } }"
    TestChecker.checkChecker(source, "MustInLoop(Continue())")

# ---- Switch Statement Errors (test_471 - test_480) ----

def test_471():
    # switch on an i32 with matching i32 case literals is legal
    source = "fn main() { switch 1 { case 1: println_i32(1); default: println_i32(0); } }"
    TestChecker.checkChecker(source, "Success")

def test_472():
    # switch on a bool with matching bool case literals is legal
    source = "fn main() { switch true { case true: println_i32(1); default: println_i32(0); } }"
    TestChecker.checkChecker(source, "Success")

def test_473():
    # switch controlling expression is neither i32 nor bool
    source = "fn main() { switch 1.0 { case 1: println_i32(1); } }"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(Switch(FloatLiteral(1.0), [Case(IntLiteral(1), [ExprStmt(CallExpr(Id(println_i32), [IntLiteral(1)]))])]))")

def test_474():
    # case literal type does not match the controlling expression's type
    source = "fn main() { let check: bool = true; switch check { case 1: println_i32(1); } }"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(Switch(Id(check), [Case(IntLiteral(1), [ExprStmt(CallExpr(Id(println_i32), [IntLiteral(1)]))])]))")

def test_475():
    # a switch with the default clause written before its case clauses is legal
    source = "fn main() { switch 1 { default: println_i32(0); case 1: println_i32(1); } }"
    TestChecker.checkChecker(source, "Success")

def test_476():
    # adjacent cases with an empty body fall through legally
    source = "fn main() { let mut y = 0; switch 1 { case 1: case 2: y = 1; default: y = 0; } }"
    TestChecker.checkChecker(source, "Success")

def test_477():
    # two cases in the same switch cannot redeclare the same variable name
    source = "fn main() { switch 1 { case 1: let v = 1; case 2: let v = 2; } }"
    TestChecker.checkChecker(source, "Redeclared(Variable, v)")

def test_478():
    # a variable declared in an earlier case is visible to a later case (shared scope)
    source = "fn main() { switch 1 { case 1: let v = 1; case 2: println_i32(v); } }"
    TestChecker.checkChecker(source, "Success")

def test_479():
    # a return statement inside a switch case is legal
    source = "fn f() -> i32 { switch 1 { case 1: return 1; default: return 0; } return 0; } fn main() {}"
    TestChecker.checkChecker(source, "Success")

def test_480():
    # nested for, switch, if, and while statements share variables correctly
    source = """
fn main() {
    let mut total = 0;
    for i in 0..4 {
        switch i {
            case 0:
                total = total + 1;
                break;
            case 1:
                if i == 1 { total = total + 2; }
                break;
            default:
                let mut j = 0;
                while j < i {
                    total = total + j;
                    j = j + 1;
                }
                break;
        }
    }
    println_i32(total);
}
"""
    TestChecker.checkChecker(source, "Success")

# ---- Function Call Errors (test_481 - test_488) ----

def test_481():
    # calling an undeclared function
    source = "fn main() { unknown_fn(1); }"
    TestChecker.checkChecker(source, "UndeclaredFunction(unknown_fn)")

def test_482():
    # calling a function with too few arguments
    source = "fn add(a: i32, b: i32) -> i32 { return a + b; } fn main() { let x = add(1); }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(CallExpr(Id(add), [IntLiteral(1)]))")

def test_483():
    # calling a function with an argument of the wrong type
    source = "fn add(a: i32, b: i32) -> i32 { return a + b; } fn main() { let x = add(1, true); }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(CallExpr(Id(add), [IntLiteral(1), BoolLiteral(True)]))")

def test_484():
    # function arguments require exact types; i32 does not coerce to f32
    source = "fn scale(a: f32) -> f32 { return a; } fn main() { let x = scale(1); }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(CallExpr(Id(scale), [IntLiteral(1)]))")

def test_485():
    # calling a built-in with the correct argument type is legal
    source = "fn main() { print_i32(1); }"
    TestChecker.checkChecker(source, "Success")

def test_486():
    # calling a built-in with the wrong argument type
    source = "fn main() { print_i32(true); }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(CallExpr(Id(print_i32), [BoolLiteral(True)]))")

def test_487():
    # using a function call's return value inside a larger expression
    source = "fn one() -> i32 { return 1; } fn main() { let x = one() + 1; }"
    TestChecker.checkChecker(source, "Success")

def test_488():
    # mutually recursive functions are legal because all signatures are collected first
    source = """
fn is_even(n: i32) -> bool {
    if n == 0 { return true; }
    return is_odd(n - 1);
}
fn is_odd(n: i32) -> bool {
    if n == 0 { return false; }
    return is_even(n - 1);
}
fn main() {
    println_bool(is_even(10));
}
"""
    TestChecker.checkChecker(source, "Success")

# ---- Other Semantic Errors (test_489 - test_500) ----

def test_489():
    # program with no main function at all
    source = "fn helper() {}"
    TestChecker.checkChecker(source, "UndeclaredFunction(main)")

def test_490():
    # main exists, but its parameter list violates the required signature
    source = "fn main(x: i32) {}"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(FuncDecl(Id(main), [VarDecl(Id(x), IntType, None, False)], VoidType, Block([])))")

def test_491():
    # main exists, but its return type violates the required signature
    source = "fn main() -> i32 { return 0; }"
    TestChecker.checkChecker(source, "TypeMismatchInStatement(FuncDecl(Id(main), [], IntType, Block([Return(IntLiteral(0))])))")

def test_492():
    # a VarDecl AST node with neither an explicit type nor an initializer (unreachable through the grammar, exercised directly at the AST level)
    ast_obj = Program([FuncDecl(Id("main"), [], VoidType,
                        Block([VarDecl(Id("x"), None, None, False)]))])
    TestChecker.checkChecker(ast_obj, "TypeCannotBeInferred(VarDecl(Id(x), None, None, False))")

def test_493():
    # empty array literal with no declared type cannot be inferred
    source = "fn main() { let x = []; }"
    TestChecker.checkChecker(source, "TypeCannotBeInferred(VarDecl(Id(x), None, ArrayLiteral([]), False))")

def test_494():
    # empty array literal against an explicit zero-size declared type is legal
    source = "fn main() { let x: [i32; 0] = []; }"
    TestChecker.checkChecker(source, "Success")

def test_495():
    # nested array inference rejects rows with different lengths
    source = "fn main() { let matrix = [[1, 2], [3, 4, 5]]; }"
    TestChecker.checkChecker(
        source,
        "TypeMismatchInExpression(ArrayLiteral([ArrayLiteral([IntLiteral(1), IntLiteral(2)]), ArrayLiteral([IntLiteral(3), IntLiteral(4), IntLiteral(5)])]))",
    )

def test_496():
    # indexing an array with a non-i32 index
    source = "fn main() { let a: [i32; 3] = [1, 2, 3]; let y = a[true]; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(ArrayCell(Id(a), BoolLiteral(True)))")

def test_497():
    # indexing a non-array value
    source = "fn main() { let x = 1; let y = x[0]; }"
    TestChecker.checkChecker(source, "TypeMismatchInExpression(ArrayCell(Id(x), IntLiteral(0)))")

def test_498():
    # nested arrays can be mutated, indexed, and passed to a function
    source = """
fn row_sum(row: [i32; 2]) -> i32 {
    return row[0] + row[1];
}
fn main() {
    let mut matrix: [[i32; 2]; 2] = [[1, 2], [3, 4]];
    matrix[0][1] = 5;
    println_i32(row_sum(matrix[0]));
}
"""
    TestChecker.checkChecker(source, "Success")

def test_499():
    # a larger valid program combining structs, loops, calls, and switch
    source = """
struct Point { x: i32, y: i32 }
fn dist(p: Point) -> i32 { return p.x + p.y; }
fn main() {
    let mut total = 0;
    for i in 0..3 {
        let p = Point { x: i, y: i };
        switch i {
            case 0: total = total + dist(p);
            default: total = total + 1;
        }
    }
    println_i32(total);
}
"""
    TestChecker.checkChecker(source, "Success")

def test_500():
    # a void-returning call cannot provide an inferred variable type
    source = "fn main() { let x = println(); }"
    TestChecker.checkChecker(
        source,
        "TypeCannotBeInferred(VarDecl(Id(x), None, CallExpr(Id(println), []), False))",
    )
