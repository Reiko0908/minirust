import pytest
from TestUtils import TestParser


# ================================================================
# STRUCT DECLARATIONS (test_201 – test_210)
# ================================================================
def test_201():
    # Trailing comma after last struct field
    TestParser.checkParser("struct Foo {\nx: i32,\n}", 3)


def test_202():
    # Missing colon in field declaration
    TestParser.checkParser("struct Foo {\nx i32\n}", 2)


def test_203():
    # Missing closing brace – next struct keyword appears instead
    TestParser.checkParser("struct Foo {\nx: i32\nstruct Bar {\ny: f32\n}", 3)


def test_204():
    # Empty struct body – at least one field required
    TestParser.checkParser("struct Foo {}", 1)


def test_205():
    # Semicolon used as field separator instead of comma
    TestParser.checkParser("struct Foo {\nx: i32;\ny: f32\n}", 2)


def test_206():
    # Missing field name – colon appears where ID is expected
    TestParser.checkParser("struct Foo {\n: i32\n}", 2)


def test_207():
    # Missing field type after colon
    TestParser.checkParser("struct Foo {\nx:\n}", 3)


def test_208():
    # Missing struct name – opening brace right after struct keyword
    TestParser.checkParser("struct {\nx: i32\n}", 1)


def test_209():
    # Missing opening brace after struct name
    TestParser.checkParser("struct Foo\nx: i32\n}", 2)


def test_210():
    # Second struct declaration missing its name
    TestParser.checkParser("struct Foo {\nx: i32\n}\nstruct {\ny: f32\n}", 4)


# ================================================================
# FUNCTION DECLARATIONS (test_211 – test_225)
# ================================================================
def test_211():
    # Missing function name – opening paren right after fn
    TestParser.checkParser("fn (a: i32) -> i32 {\nreturn a;\n}", 1)


def test_212():
    # Missing opening paren – identifier appears instead
    TestParser.checkParser("fn foo a: i32) -> i32 {\nreturn a;\n}", 1)


def test_213():
    # Missing closing paren – arrow appears before paren closes
    TestParser.checkParser("fn foo(a: i32 -> i32 {\nreturn a;\n}", 1)


def test_214():
    # Missing opening brace for function body
    TestParser.checkParser("fn foo(a: i32) -> i32\nreturn a;\n}", 2)


def test_215():
    # Missing closing brace – next fn keyword appears inside body
    TestParser.checkParser("fn foo() -> i32 {\nreturn 1;\nfn bar() {}", 3)


def test_216():
    # Parameter missing colon between name and type
    TestParser.checkParser("fn foo(a i32) -> i32 {\nreturn a;\n}", 1)


def test_217():
    # Arrow present but return type missing – brace appears instead
    TestParser.checkParser("fn foo(a: i32) -> {\nreturn a;\n}", 1)


def test_218():
    # Return type missing after arrow on next line
    TestParser.checkParser("fn foo(a: i32) ->\n{\nreturn a;\n}", 2)


def test_219():
    # Nested function definition inside a function body
    TestParser.checkParser("fn outer() {\nfn inner() {\n}\n}", 2)


def test_220():
    # Trailing comma at end of parameter list
    TestParser.checkParser("fn foo(a: i32, b: i32,) -> i32 {\nreturn a;\n}", 1)


def test_221():
    # Parameter declared without a type
    TestParser.checkParser("fn foo(a) -> i32 {\nreturn a;\n}", 1)


def test_222():
    # Semicolon used instead of block for function body
    TestParser.checkParser("fn foo(a: i32) -> i32;", 1)


def test_223():
    # Double arrow in return type position
    TestParser.checkParser("fn foo() -> -> i32 {\nreturn 1;\n}", 1)


def test_224():
    # Two type names after the arrow – only one allowed
    TestParser.checkParser("fn foo() -> i32 f32 {\nreturn 1;\n}", 1)


def test_225():
    # Opening paren immediately followed by arrow – param list broken
    TestParser.checkParser("fn foo( -> i32 {\nreturn 1;\n}", 1)


# ================================================================
# VARIABLE DECLARATIONS (test_226 – test_245)
# ================================================================
def test_226():
    # Variable declaration missing its terminating semicolon
    TestParser.checkParser("fn main() {\nlet x = 5\n}", 3)


def test_227():
    # Missing variable name – assignment operator appears after let
    TestParser.checkParser("fn main() {\nlet = 5;\n}", 2)


def test_228():
    # Comma-separated multiple variables in a single let – not allowed
    TestParser.checkParser("fn main() {\nlet x, y = 5;\n}", 2)


def test_229():
    # Typed declaration missing the = sign before initializer
    TestParser.checkParser("fn main() {\nlet x: i32 5;\n}", 2)


def test_230():
    # Missing type name after the colon
    TestParser.checkParser("fn main() {\nlet x: = 5;\n}", 2)


def test_231():
    # Keyword let used as a type name
    TestParser.checkParser("fn main() {\nlet x: let = 5;\n}", 2)


def test_232():
    # Array type uses comma as separator instead of semicolon
    TestParser.checkParser("fn main() {\nlet x: [i32, 3] = [1, 2, 3];\n}", 2)


def test_233():
    # Array type missing the integer size literal
    TestParser.checkParser("fn main() {\nlet x: [i32;] = [];\n}", 2)


def test_234():
    # Array type missing the element type before semicolon
    TestParser.checkParser("fn main() {\nlet x: [; 3] = [];\n}", 2)


def test_235():
    # Array type missing closing bracket – equals sign appears instead
    TestParser.checkParser("fn main() {\nlet x: [i32; 3 = [1, 2, 3];\n}", 2)


def test_236():
    # mut keyword used standalone without let
    TestParser.checkParser("fn main() {\nmut x = 5;\n}", 2)


def test_237():
    # Type-inferred declaration with missing initializer expression
    TestParser.checkParser("fn main() {\nlet x =;\n}", 2)


def test_238():
    # Missing semicolon after typed mutable declaration
    TestParser.checkParser("fn main() {\nlet mut x: i32\nlet y = 5;\n}", 3)


def test_239():
    # Double colon in type annotation
    TestParser.checkParser("fn main() {\nlet x: i32: i32 = 5;\n}", 2)


def test_240():
    # Array size specified as a float literal instead of integer
    TestParser.checkParser("fn main() {\nlet x: [i32; 3.0] = [1, 2, 3];\n}", 2)


def test_241():
    # let mut with colon immediately after mut – name is missing
    TestParser.checkParser("fn main() {\nlet mut: i32 = 5;\n}", 2)


def test_242():
    # Reserved keyword if used as the variable name
    TestParser.checkParser("fn main() {\nlet if = 5;\n}", 2)


def test_243():
    # Array type with two semicolons – extra dimension not allowed
    TestParser.checkParser("fn main() {\nlet x: [i32; 2; 3] = [];\n}", 2)


def test_244():
    # Missing semicolon – next let seen where semicolon expected
    TestParser.checkParser("fn main() {\nlet x = 5\nlet y = 10;\n}", 3)


def test_245():
    # Array size given as negated expression – INT_LIT token required
    TestParser.checkParser("fn main() {\nlet x: [i32; -3] = [];\n}", 2)


# ================================================================
# CONTROL FLOW STRUCTURES (test_246 – test_260)
# ================================================================
def test_246():
    # if with no condition – opening brace where expression expected
    TestParser.checkParser("fn main() {\nif {\nlet x = 1;\n}\n}", 2)


def test_247():
    # if condition present but no block – let statement instead of brace
    TestParser.checkParser("fn main() {\nif true\nlet x = 1;\n}", 3)


def test_248():
    # else keyword used without a preceding if
    TestParser.checkParser("fn main() {\nelse {\nlet x = 1;\n}\n}", 2)


def test_249():
    # while with no condition – opening brace instead of expression
    TestParser.checkParser("fn main() {\nwhile {\nlet x = 1;\n}\n}", 2)


def test_250():
    # while condition present but no block – let appears instead of brace
    TestParser.checkParser("fn main() {\nwhile true\nlet x = 1;\n}", 3)


def test_251():
    # for loop missing the in keyword
    TestParser.checkParser("fn main() {\nfor i 0..10 {\n}\n}", 2)


def test_252():
    # for loop missing the range operator ..
    TestParser.checkParser("fn main() {\nfor i in 0 10 {\n}\n}", 2)


def test_253():
    # for loop body replaced with semicolon
    TestParser.checkParser("fn main() {\nfor i in 0..10;\n}", 2)


def test_254():
    # break statement missing its semicolon
    TestParser.checkParser("fn main() {\nwhile true {\nbreak\n}\n}", 4)


def test_255():
    # continue statement missing its semicolon
    TestParser.checkParser("fn main() {\nwhile true {\ncontinue\n}\n}", 4)


def test_256():
    # return statement missing its semicolon
    TestParser.checkParser("fn foo() -> i32 {\nreturn 1\n}", 3)


def test_257():
    # else clause present but its block is missing
    TestParser.checkParser("fn main() {\nif true {\n} else\n}", 4)


def test_258():
    # for loop variable name is the reserved keyword if
    TestParser.checkParser("fn main() {\nfor if in 0..10 {\n}\n}", 2)


def test_259():
    # while condition on next line – brace parsed where expression expected
    TestParser.checkParser("fn main() {\nwhile\n{\n}\n}", 3)


def test_260():
    # else if branch has no condition – brace appears instead of expression
    TestParser.checkParser("fn main() {\nif true {\n} else if {\n}\n}", 3)


# ================================================================
# SWITCH STATEMENTS (test_261 – test_270)
# ================================================================
def test_261():
    # switch with no expression – opening brace where expression expected
    TestParser.checkParser("fn main() {\nswitch {\ncase 1:\nbreak;\n}\n}", 2)


def test_262():
    # switch body completely empty – switchItem+ requires at least one
    TestParser.checkParser("fn main() {\nswitch x {\n}\n}", 3)


def test_263():
    # case clause missing its colon after the literal
    TestParser.checkParser("fn main() {\nswitch x {\ncase 1\nbreak;\n}\n}", 4)


def test_264():
    # case clause with no literal – colon appears immediately after case
    TestParser.checkParser("fn main() {\nswitch x {\ncase :\nbreak;\n}\n}", 3)


def test_265():
    # default clause missing its colon
    TestParser.checkParser(
        "fn main() {\nswitch x {\ncase 0:\nbreak;\ndefault\nbreak;\n}\n}", 6
    )


def test_266():
    # switch body closing brace missing – fn keyword appears instead
    TestParser.checkParser("fn main() {\nswitch x {\ncase 1:\nbreak;\nfn bar() {}", 5)


def test_267():
    # switch body opening brace is missing
    TestParser.checkParser("fn main() {\nswitch x\ncase 1:\nbreak;\n}\n}", 3)


def test_268():
    # case value is a compound expression, not a single literal
    TestParser.checkParser("fn main() {\nswitch x {\ncase 1 + 1:\nbreak;\n}\n}", 3)


def test_269():
    # bare semicolon appears between case items in switch body
    TestParser.checkParser(
        "fn main() {\nswitch x {\ncase 0:\nbreak;\n;\ndefault:\nbreak;\n}\n}", 5
    )


def test_270():
    # match keyword (unknown identifier) used instead of switch
    TestParser.checkParser("fn main() {\nmatch x {\ncase 1:\nbreak;\n}\n}", 2)


# ================================================================
# EXPRESSION PRECEDENCES (test_271 – test_285)
# ================================================================
def test_271():
    # Chained relational: a < b < c is non-associative – syntax error
    TestParser.checkParser("fn main() {\nlet x = a < b < c;\n}", 2)


def test_272():
    # Chained equality: a == b == c is non-associative – syntax error
    TestParser.checkParser("fn main() {\nlet x = a == b == c;\n}", 2)


def test_273():
    # Missing right operand after binary + operator
    TestParser.checkParser("fn main() {\nlet x = 5 +;\n}", 2)


def test_274():
    # Double multiplication operator – second * cannot start an expression
    TestParser.checkParser("fn main() {\nlet x = 5 * * 3;\n}", 2)


def test_275():
    # Missing closing parenthesis in grouped expression
    TestParser.checkParser("fn main() {\nlet x = (5 + 3;\n}", 2)


def test_276():
    # Missing closing bracket in array index expression
    TestParser.checkParser("fn main() {\nlet x = arr[0;\n}", 2)


def test_277():
    # Unary plus is not a valid operator in MiniRust
    TestParser.checkParser("fn main() {\nlet x = +5;\n}", 2)


def test_278():
    # Chained relational: a >= b >= c is non-associative
    TestParser.checkParser("fn main() {\nlet x = a >= b >= c;\n}", 2)


def test_279():
    # Chained inequality: a != b != c is non-associative
    TestParser.checkParser("fn main() {\nlet x = a != b != c;\n}", 2)


def test_280():
    # Assignment with missing right-hand side expression
    TestParser.checkParser("fn main() {\na =;\n}", 2)


def test_281():
    # Expression statement starting with * operator – cannot begin expression
    TestParser.checkParser("fn main() {\n* 5;\n}", 2)


def test_282():
    # Expression composed entirely of operators with no operands
    TestParser.checkParser("fn main() {\nlet x = * + -;\n}", 2)


def test_283():
    # Expression statement missing semicolon – let appears on next line
    TestParser.checkParser("fn main() {\n5 + 3\nlet x = 1;\n}", 3)


def test_284():
    # Chained relational: a <= b <= c is non-associative
    TestParser.checkParser("fn main() {\nlet x = a <= b <= c;\n}", 2)


def test_285():
    # Chained relational: a > b > c is non-associative
    TestParser.checkParser("fn main() {\nlet x = a > b > c;\n}", 2)


# ================================================================
# PRIMARY & COMPLEX ACCESSES (test_286 – test_295)
# ================================================================
def test_286():
    # Array literal missing its closing bracket
    TestParser.checkParser("fn main() {\nlet x = [1, 2, 3;\n}", 2)


def test_287():
    # Struct initializer missing its closing brace
    TestParser.checkParser("fn main() {\nlet p = Point { x: 1, y: 2;\n}", 2)


def test_288():
    # Struct initializer with no fields – at least one initializer required
    TestParser.checkParser("fn main() {\nlet p = Point {};\n}", 2)


def test_289():
    # Function call with trailing comma after last argument
    TestParser.checkParser("fn main() {\nfoo(1, 2,);\n}", 2)


def test_290():
    # Outer array index missing closing bracket after inner index expr
    TestParser.checkParser("fn main() {\nlet x = arr[arr2[0];\n}", 2)


def test_291():
    # Member access dot operator with no field name following it
    TestParser.checkParser("fn main() {\nlet x = p.;\n}", 2)


def test_292():
    # Function call argument list starts with comma – no leading expression
    TestParser.checkParser("fn main() {\nfoo(,);\n}", 2)


def test_293():
    # Array literal has an empty slot between two commas
    TestParser.checkParser("fn main() {\nlet x = [1, , 3];\n}", 2)


def test_294():
    # Struct field initializer missing its value expression
    TestParser.checkParser("fn main() {\nlet p = Point { x:, y: 2 };\n}", 2)


def test_295():
    # Double-dot range operator used where member access (DOT ID) is expected
    TestParser.checkParser("fn main() {\nlet x = p..x;\n}", 2)


# ================================================================
# INTEGRATED PROGRAMS (test_296 – test_300)
# ================================================================
def test_296():
    # Global variable declaration at file scope – not permitted
    TestParser.checkParser("let x = 5;\nfn main() {\n}", 1)


def test_297():
    # Struct definition appears after a function definition – wrong order
    TestParser.checkParser("fn main() {\n}\nstruct Point {\nx: i32\n}", 3)


def test_298():
    # Nested function definition inside a function body – not allowed
    TestParser.checkParser("fn outer() {\nfn inner() {\n}\n}", 2)


def test_299():
    # Top-level expression statement outside any function
    TestParser.checkParser("fn main() {\n}\nlet x = 5;", 3)


def test_300():
    # Main function body missing its closing brace – EOF encountered
    TestParser.checkParser("fn main() {\nlet x = 5;\n", 3)
