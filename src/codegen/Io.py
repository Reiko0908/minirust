"""
I/O symbol definitions for built-in functions.
"""

from utils.AST import IntType, FloatType, StringType, VoidType, BoolType
from codegen.Utils import FunctionType, Symbol, CName


LIB_NAME = "io"

# Built-in functions:
IO_SYMBOL_LIST = [
    # MiniRust specification functions
    Symbol("print_i32", FunctionType([IntType()], VoidType()), CName(LIB_NAME)),
    Symbol("println_i32", FunctionType([IntType()], VoidType()), CName(LIB_NAME)),
    Symbol("print_f32", FunctionType([FloatType()], VoidType()), CName(LIB_NAME)),
    Symbol("println_f32", FunctionType([FloatType()], VoidType()), CName(LIB_NAME)),
    Symbol("print_bool", FunctionType([BoolType()], VoidType()), CName(LIB_NAME)),
    Symbol("println_bool", FunctionType([BoolType()], VoidType()), CName(LIB_NAME)),
    Symbol("print_string", FunctionType([StringType()], VoidType()), CName(LIB_NAME)),
    Symbol("println_string", FunctionType([StringType()], VoidType()), CName(LIB_NAME)),
    Symbol("println", FunctionType([], VoidType()), CName(LIB_NAME)),
]
