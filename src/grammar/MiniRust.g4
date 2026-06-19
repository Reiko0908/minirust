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

// ================================
// Lexer Rules
// ================================
// --------------------------------
// Keywords
// --------------------------------
LET           : 'let';
MUT           : 'mut';
FN            : 'fn';
STRUCT        : 'struct';
IF            : 'if';
ELSE          : 'else';
WHILE         : 'while';
FOR           : 'for';
IN            : 'in';
BREAK         : 'break';
CONTINUE      : 'continue';
SWITCH        : 'switch';
CASE          : 'case';
DEFAULT       : 'default';
RETURN        : 'return';
I32           : 'i32';
F32           : 'f32';
BOOL          : 'bool';
VOID          : 'void';
STRING        : 'string';
TRUE          : 'true';
FALSE         : 'false';

// --------------------------------
// OPERATORS & PUNCTUATORS
// --------------------------------
ARROW         : '->';
RANGE         : '..';

EQ            : '==';
NEQ           : '!=';
LEQ           : '<=';
GEQ           : '>=';
AND           : '&&';
OR            : '||';

LT            : '<';
GT            : '>';
NOT           : '!';
ASSIGN        : '=';

PLUS          : '+';
MINUS         : '-';
MUL           : '*';
DIV           : '/';
MOD           : '%';

SEMI          : ';';
COMMA         : ',';
COLON         : ':';
DOT           : '.';

LPAREN        : '(';
RPAREN        : ')';
LBRACE        : '{';
RBRACE        : '}';
LBRACK        : '[';
RBRACK        : ']';

// --------------------------------
// LITERALS
// --------------------------------
fragment Digit: [0-9]+;
fragment Exp  : [eE] [+-]? Digits;
fragment Esc  : '\\' ('n' | 't' | '"' | '\\');

BIN_LIT       : '0'[Bb][01]+;
OCT_LIT       : '0'[0-7]+;
HEX_LIT       : '0'[xX][0-9a-fA-F]+;
INT_LIT       : Digits;

FLOAT_LIT     : Digits '.' Digits Exp? | Digits Exp;
STRING_LIT    : '"' (Esc | ~["\\\r\n])*? '"';

// --------------------------------
// IDENTIFIER
// --------------------------------
ID            : [a-zA-Z_][a-zA-Z0-9]*;

// --------------------------------
// COMMENTS & WHITESPACE
// --------------------------------
CMT_LINE      : '//' ~[\r\n]* -> skip;
CMT_BLOCK     : '/*' .*? '*/' -> skip;
WS            : [ \t\r\n]+ -> skip;

// --------------------------------
// LEXICAL ERROR
// --------------------------------
ERROR_TOKEN   : . { raise ErrorToken(self.text, self.line) };
