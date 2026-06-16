import pytest
from TestUtils import TestParser

def test_201():
    # Missing function name
    TestParser.checkParser("fn() { print(1); }", 1)

def test_202():
    # Missing parameter parentheses
    TestParser.checkParser("fn main { print(1); }", 1)

def test_203():
    # Missing body block braces
    TestParser.checkParser("fn main() print(1);", 1)

def test_204():
    # Missing statement semicolon
    TestParser.checkParser("fn main() { print(1) }", 1)

def test_205():
    # Missing fn keyword
    TestParser.checkParser("main() { print(1); }", 1)
