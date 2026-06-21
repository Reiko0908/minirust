from TestUtils import TestLexer


# =====================================================================
# KEYWORDS (test_101 - test_110)
# =====================================================================
def test_101():
    # Keyword: mutable variable declaration.
    TestLexer.checkLexer("let mut", "let, mut")


def test_102():
    # Keyword: function and struct declarations.
    TestLexer.checkLexer("fn struct", "fn, struct")


def test_103():
    # Keyword: if-else conditional.
    TestLexer.checkLexer("if else", "if, else")


def test_104():
    # Keyword: loop constructs.
    TestLexer.checkLexer("while for in", "while, for, in")


def test_105():
    # Keyword: jump and return statements.
    TestLexer.checkLexer("break continue return", "break, continue, return")


def test_106():
    # Keyword: switch-case constructs.
    TestLexer.checkLexer("switch case default", "switch, case, default")


def test_107():
    # Keyword: primitive types.
    TestLexer.checkLexer("i32 f32 bool", "i32, f32, bool")


def test_108():
    # Keyword: void and string types.
    TestLexer.checkLexer("void string", "void, string")


def test_109():
    # Keyword: boolean literals.
    TestLexer.checkLexer("true false", "true, false")


def test_110():
    # All 22 reserved keywords in one pass.
    TestLexer.checkLexer(
        "let mut fn struct if else while for in break continue switch case default return i32 f32 bool void string true false",
        "let, mut, fn, struct, if, else, while, for, in, break, continue, switch, case, default, return, i32, f32, bool, void, string, true, false",
    )


# =====================================================================
# IDENTIFIERS (test_111 - test_120)
# =====================================================================
def test_111():
    # Basic identifier names.
    TestLexer.checkLexer("foo main", "foo, main")


def test_112():
    # Identifiers with underscores in the middle.
    TestLexer.checkLexer("my_var value__type", "my_var, value__type")


def test_113():
    # Identifiers starting with underscores.
    TestLexer.checkLexer("_hidden __builtin", "_hidden, __builtin")


def test_114():
    # Identifiers that are just underscores.
    TestLexer.checkLexer("_ __", "_, __")


def test_115():
    # Identifiers mixed with trailing digits.
    TestLexer.checkLexer("foo1 bar2 baz3x", "foo1, bar2, baz3x")


def test_116():
    # Keyword-prefixed identifiers are not split into keyword + ID.
    TestLexer.checkLexer("is_true mystruct", "is_true, mystruct")


def test_117():
    # Identifiers combining underscores and digits.
    TestLexer.checkLexer(
        "_temp1 user_Id2 total_Count3_", "_temp1, user_Id2, total_Count3_"
    )


def test_118():
    # Single-character and edge-case identifiers.
    TestLexer.checkLexer("a _A Z _36 z_", "a, _A, Z, _36, z_")


def test_119():
    # Identifiers cannot start with a digit, so leading digits split off.
    TestLexer.checkLexer(
        "123foo 0x_val 253semester", "123, foo, 0, x_val, 253, semester"
    )


def test_120():
    # Standard library identifiers containing digits lex as single tokens.
    TestLexer.checkLexer(
        "print_i32 println_f32 print_string", "print_i32, println_f32, print_string"
    )


# =====================================================================
# VALID & SIGNED NUMBERS (test_121 - test_140)
# =====================================================================
def test_121():
    # Zero literal alone.
    TestLexer.checkLexer("0", "0")


def test_122():
    # Single-digit integer literal.
    TestLexer.checkLexer("7", "7")


def test_123():
    # Multi-digit integer literal.
    TestLexer.checkLexer("2026", "2026")


def test_124():
    # Integer literal with leading zeros stays decimal.
    TestLexer.checkLexer("0036", "0036")


def test_125():
    # Signed integer is unary minus plus an integer literal, not one token.
    TestLexer.checkLexer("-150", "-, 150")


def test_126():
    # Float literal in standard fractional notation.
    TestLexer.checkLexer("3.14", "3.14")


def test_127():
    # Float literal with a leading zero before the point.
    TestLexer.checkLexer("0.5", "0.5")


def test_128():
    # Float literal with zeros on both sides of the point.
    TestLexer.checkLexer("0.00", "0.00")


def test_129():
    # Float literal with multiple digits on both sides.
    TestLexer.checkLexer("253.367", "253.367")


def test_130():
    # Signed float is unary minus plus a float literal, not one token.
    TestLexer.checkLexer("-2.5", "-, 2.5")


def test_131():
    # Scientific notation with lowercase e.
    TestLexer.checkLexer("1e10", "1e10")


def test_132():
    # Scientific notation with uppercase E.
    TestLexer.checkLexer("1E10", "1E10")


def test_133():
    # Scientific notation with an explicit plus sign.
    TestLexer.checkLexer("2e+3", "2e+3")


def test_134():
    # Scientific notation with a fractional part and a minus sign.
    TestLexer.checkLexer("3.14e-5", "3.14e-5")


def test_135():
    # An operator right after the exponent digits must not merge into the literal.
    TestLexer.checkLexer("3E6+7", "3E6, +, 7")


def test_136():
    # Signed float literal in scientific notation.
    TestLexer.checkLexer("-6.022e-23", "-, 6.022e-23")


def test_137():
    # Multiple numeric literals separated by whitespace.
    TestLexer.checkLexer("1 2.5 3e4", "1, 2.5, 3e4")


def test_138():
    # Integer literal directly adjacent to an operator with no merging.
    TestLexer.checkLexer("10+20", "10, +, 20")


def test_139():
    # The range operator must not be mistaken for a decimal point.
    TestLexer.checkLexer("1..5", "1, .., 5")


def test_140():
    # A very large integer literal with no length limit.
    TestLexer.checkLexer("123456789012345", "123456789012345")


# =====================================================================
# INVALID NUMBERS (test_141 - test_150)
# =====================================================================
def test_141():
    # Multiple decimal points split into a float and a separate dot.
    TestLexer.checkLexer("1.2.3", "1.2, ., 3")


def test_142():
    # A trailing dot with nothing after it splits off on its own.
    TestLexer.checkLexer("1.2.", "1.2, .")


def test_143():
    # Missing digits after the decimal point leaves the dot as its own token.
    TestLexer.checkLexer("5.", "5, .")


def test_144():
    # Missing digits before the decimal point leaves the dot as its own token.
    TestLexer.checkLexer(".5", "., 5")


def test_145():
    # An exponent marker with no digits after it is not part of the number.
    TestLexer.checkLexer("1e", "1, e")


def test_146():
    # An exponent sign with no digits after it is not part of the number.
    TestLexer.checkLexer("1e+", "1, e, +")


def test_147():
    # A second exponent marker is not absorbed into the first float.
    TestLexer.checkLexer("1e1e1", "1e1, e1")


def test_148():
    # A double minus sign breaks exponent matching entirely.
    TestLexer.checkLexer("12e--3", "12, e, -, -, 3")


def test_149():
    # No digit after the decimal point blocks the exponent from attaching.
    TestLexer.checkLexer("5.e3", "5, ., e3")


def test_150():
    # A leading dot still can't attach to a valid scientific-notation tail.
    TestLexer.checkLexer(".5e3", "., 5e3")


# =====================================================================
# VALID STRINGS & ESCAPES (test_151 - test_160)
# =====================================================================
def test_151():
    # Empty string literal.
    TestLexer.checkLexer('""', '""')


def test_152():
    # Simple string content with no escapes.
    TestLexer.checkLexer('"hello"', '"hello"')


def test_153():
    # String content containing embedded spaces.
    TestLexer.checkLexer('"hello world!"', '"hello world!"')


def test_154():
    # String literal using the newline escape sequence.
    TestLexer.checkLexer(r'"line1\nline2"', r'"line1\nline2"')


def test_155():
    # String literal using the tab escape sequence.
    TestLexer.checkLexer(r'"col1\tcol2"', r'"col1\tcol2"')


def test_156():
    # String literal using the escaped double-quote sequence.
    TestLexer.checkLexer(r'"Calling function \"main\""', r'"Calling function \"main\""')


def test_157():
    # String literal using the escaped backslash sequence.
    TestLexer.checkLexer(r'"src\\grammar\\MiniRust.g4"', r'"src\\grammar\\MiniRust.g4"')


def test_158():
    # String literal combining all four supported escape sequences.
    TestLexer.checkLexer(
        r'"Error:\n\tFile \"src\\grammar\\MiniRust.g4\""',
        r'"Error:\n\tFile \"src\\grammar\\MiniRust.g4\""',
    )


def test_159():
    # Keywords, operators, and punctuation are ordinary characters inside strings.
    TestLexer.checkLexer('"let mut x = 10 + 20;"', '"let mut x = 10 + 20;"')


def test_160():
    # Consecutive string literals are not merged.
    TestLexer.checkLexer(
        '"Error: ""undefined variable"', '"Error: ", "undefined variable"'
    )


# =====================================================================
# STRING ERRORS (test_161 - test_175)
# =====================================================================
def test_161():
    # Unclosed string cut off by a real newline.
    TestLexer.checkLexer('"abc\ndef"', "Unclosed String: abc")


def test_162():
    # Unclosed string cut off by EOF with no newline at all.
    TestLexer.checkLexer('"abc', "Unclosed String: abc")


def test_163():
    # Unclosed empty string cut off immediately by a newline.
    TestLexer.checkLexer('"\n', "Unclosed String: ")


def test_164():
    # Unclosed string with a valid escape, cut off by a newline.
    TestLexer.checkLexer('"abc\\tdef\n<newline>', r"Unclosed String: abc\tdef")


def test_165():
    # Unclosed string with a valid escape, cut off by EOF.
    TestLexer.checkLexer('"abc\\tdef', r"Unclosed String: abc\tdef")


def test_166():
    # Unclosed string with nothing but the opening quote before EOF.
    TestLexer.checkLexer('"', "Unclosed String: ")


def test_167():
    # Illegal escape: backslash followed by a disallowed letter.
    TestLexer.checkLexer(r'"bad\dval"', r"Illegal Escape In String: bad\d")


def test_168():
    # Illegal escape: backslash followed by a digit.
    TestLexer.checkLexer(
        r'"Match group: \1 found"', r"Illegal Escape In String: Match group: \1"
    )


def test_169():
    # Illegal escape: backslash followed by a plain space.
    TestLexer.checkLexer(r'"bad\ val"', "Illegal Escape In String: bad\\ ")


def test_170():
    # Illegal escape: backslash followed by r, which MiniRust does not allow.
    TestLexer.checkLexer(r'"Line1\r\nLine2"', r"Illegal Escape In String: Line1\r")


def test_171():
    # Illegal escape: backslash followed by a single quote.
    TestLexer.checkLexer(r'''"bad\'val"''', r"Illegal Escape In String: bad\'")


def test_172():
    # Illegal escape: backslash followed directly by a real newline.
    TestLexer.checkLexer(
        '"Error: invalid input,\\\nplease try again"',
        "Illegal Escape In String: Error: invalid input,\\\n",
    )


def test_173():
    # Illegal escape occurring after a valid escape earlier in the string.
    TestLexer.checkLexer(
        r'"Col1:\tCol2\vCol3"', r"Illegal Escape In String: Col1:\tCol2\v"
    )


def test_174():
    # Illegal escape correctly reports the line it occurs on, not line one.
    TestLexer.checkLexer(
        'let x = 1;\n"bad\\qval"',
        r"let, x, =, 1, ;, Illegal Escape In String: bad\q",
    )


def test_175():
    # Unclosed string correctly reports the line it begins on, not line one.
    TestLexer.checkLexer(
        'let x = 1;\nlet y = 2;\n"let z = 3;\n',
        "let, x, =, 1, ;, let, y, =, 2, ;, Unclosed String: let z = 3;",
    )


# =====================================================================
# ERROR TOKENS (test_176 - test_180)
# =====================================================================
def test_176():
    TestLexer.checkLexer("@main", "Error Token @")


def test_177():
    TestLexer.checkLexer("#include", "Error Token #")


def test_178():
    TestLexer.checkLexer("price = $100", "price, =, Error Token $")


def test_179():
    TestLexer.checkLexer("x = (a == b) ? 1 : 0;", "x, =, (, a, ==, b, ), Error Token ?")


def test_180():
    TestLexer.checkLexer("let `value` = 10;", "let, Error Token `")


# =====================================================================
# OPERATORS & PUNCTUATORS (test_181 - test_190)
# =====================================================================
def test_181():
    # Arithmetic operators.
    TestLexer.checkLexer("+ - * / %", "+, -, *, /, %")


def test_182():
    # Comparison operators.
    TestLexer.checkLexer("== != < <= > >=", "==, !=, <, <=, >, >=")


def test_183():
    # Logical operators.
    TestLexer.checkLexer("&& || !", "&&, ||, !")


def test_184():
    # Maximal munch: == must not split into two = tokens.
    TestLexer.checkLexer("a == b", "a, ==, b")


def test_185():
    # Maximal munch: three dots must split as RANGE + DOT.
    TestLexer.checkLexer("1...2", "1, .., ., 2")


def test_186():
    # Maximal munch: the arrow operator must not split into minus and greater-than.
    TestLexer.checkLexer("fn f() -> i32 {}", "fn, f, (, ), ->, i32, {, }")


def test_187():
    # Common punctuation in declarations and indexing.
    TestLexer.checkLexer(
        "arr[0]; fn main() {}", "arr, [, 0, ], ;, fn, main, (, ), {, }"
    )


def test_188():
    # Maximal munch: <= must not split into < and =.
    TestLexer.checkLexer("a<=b", "a, <=, b")


def test_189():
    # Maximal munch: != must not split into ! and =.
    TestLexer.checkLexer("a!=b", "a, !=, b")


def test_190():
    # A lone & is not a valid token since only && is defined.
    TestLexer.checkLexer("a & b", "a, Error Token &")


# =====================================================================
# COMMENTS & WHITESPACE (test_191 - test_200)
# =====================================================================
def test_191():
    # Single-line comment before a declaration.
    TestLexer.checkLexer("// initialize variables\nlet x", "let, x")


def test_192():
    # Trailing comment after a declaration.
    TestLexer.checkLexer("let x // x stores the loop counter", "let, x")


def test_193():
    # Single-line comment reaching EOF.
    TestLexer.checkLexer("let x // TODO: assign value later", "let, x")


def test_194():
    # Inline block comment between tokens.
    TestLexer.checkLexer("let /* mutable variable */ x", "let, x")


def test_195():
    # Multi-line documentation comment.
    TestLexer.checkLexer("let /* Function:\ncompute sum */ x", "let, x")


def test_196():
    # Comment used as a separator.
    TestLexer.checkLexer("/* generated code */main", "main")


def test_197():
    # Nested-looking comment closes at the first terminator.
    TestLexer.checkLexer(
        "/* TODO: /* revise later */ still active */",
        "still, active, *, /",
    )


def test_198():
    # An unclosed block comment decomposes into ordinary tokens instead of erroring.
    TestLexer.checkLexer("/* never closed", "/, *, never, closed")


def test_199():
    # Mixed tabs and spaces around an assignment.
    TestLexer.checkLexer("let\t\tcount   =\t1", "let, count, =, 1")


def test_200():
    # Comments interleaved with declarations.
    TestLexer.checkLexer(
        "let x = 1; // initialize x\n/* next variable */ let y = 2;",
        "let, x, =, 1, ;, let, y, =, 2, ;",
    )
