grammar MiniRust;

@lexer::header {
from utils.lexerror import *
}

// ====================
// Parser Rules
// ====================

program
    : funcDecl EOF
    ;

funcDecl
    : FN ID LPAREN RPAREN block
    ;

block
    : LBRACE statement RBRACE
    ;

statement
    : callExpr SEMI
    ;

callExpr
    : ID LPAREN INT_LIT RPAREN
    ;

// ====================
// Lexer Rules
// ====================

FN          : 'fn';
LPAREN      : '(';
RPAREN      : ')';
LBRACE      : '{';
RBRACE      : '}';
SEMI        : ';';
COMMA       : ',';

INT_LIT     : [0-9];
ID          : [a-zA-Z_]+ | 'print_i32';
WS          : [ \t\r\n]+ -> skip;

ERROR_TOKEN : . { raise ErrorToken(self.text, self.line) };
