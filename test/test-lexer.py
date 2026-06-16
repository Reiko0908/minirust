import pytest
from TestUtils import TestLexer

def test_101():
    # Keyword fn
    TestLexer.checkLexer("fn", "fn")

def test_102():
    # Identifiers main and print
    TestLexer.checkLexer("main print", "main, print")

def test_103():
    # Punctuators: parentheses, braces, semicolon
    TestLexer.checkLexer("() {};", "(, ), {, }, ;")

def test_104():
    # Integer literal
    TestLexer.checkLexer("1", "1")

def test_105():
    # Full minimum program token sequence
    TestLexer.checkLexer("fn main() { print(1); }", "fn, main, (, ), {, print, (, 1, ), ;, }")
