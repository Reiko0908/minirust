grammar MiniRust;

@lexer::header {
from utils.lexerror import *
}

// ================================
// Parser Rules
// ================================
program
    : structDecl* funcDecl* EOF
    ;

// --------------------------------
// Struct Declaration
// --------------------------------
structDecl
    : STRUCT ID LBRACE fieldDecl (COMMA fieldDecl)* RBRACE
    ;

fieldDecl
    : ID COLON typeName
    ;

// --------------------------------
// Function Declaration
// --------------------------------
funcDecl
    : FN ID LPAREN paramList? RPAREN (ARROW typeName)? block
    ;

paramList
    : param (COMMA param)*
    ;

param
    : ID COLON typeName
    ;

// --------------------------------
// Type
// --------------------------------
typeName
    : primitiveType
    | arrayType
    | ID
    ;

primitiveType
    : I32 | F32 | BOOL | STRING | VOID
    ;

arrayType
    : LBRACK typeName SEMI INT_LIT RBRACK
    ;

// --------------------------------
// Blocks & Statements
// --------------------------------
block
    : LBRACE (stmt | varDecl)* RBRACE
    ;

stmt
    : exprStmt
    | ifStmt
    | switchStmt
    | whileStmt
    | forStmt
    | breakStmt
    | continueStmt
    | returnStmt
    | block
    ;

varDecl
    : LET MUT? ID COLON typeName ASSIGN expr SEMI
    | LET MUT? ID COLON typeName SEMI
    | LET MUT? ID ASSIGN expr SEMI
    ;

exprStmt
    : expr SEMI
    ;

ifStmt
    : IF expr block (ELSE (block | ifStmt))?
    ;

switchStmt
    : SWITCH expr LBRACE switchItem+ RBRACE
    ;

switchItem
    : caseClause
    | defaultClause
    ;

caseClause
    : CASE literal COLON (stmt | varDecl)*
    ;

defaultClause
    : DEFAULT COLON (stmt | varDecl)*
    ;

literal
    : INT_LIT
    | FLOAT_LIT
    | STRING_LIT
    | TRUE
    | FALSE
    ;

whileStmt
    : WHILE expr block
    ;

forStmt
    : FOR ID IN expr RANGE expr block
    ;

breakStmt
    : BREAK SEMI
    ;

continueStmt
    : CONTINUE SEMI
    ;

returnStmt
    : RETURN expr? SEMI
    ;

// --------------------------------
// Expressions
// --------------------------------
expr
    : assignExpr
    ;

lvalue
    : ID (DOT ID | LBRACK expr RBRACK)*
    ;

assignExpr
    : lvalue ASSIGN assignExpr
    | orExpr
    ;

orExpr
    : andExpr (OR andExpr)*
    ;

andExpr
    : eqExpr (AND eqExpr)*
    ;

eqExpr
    : relExpr ((EQ | NEQ) relExpr)?
    ;

relExpr
    : addExpr ((LT | GT | LEQ | GEQ) addExpr)?
    ;

addExpr
    : mulExpr ((ADD | SUB) mulExpr)*
    ;

mulExpr
    : unaryExpr ((MUL | DIV | MOD) unaryExpr)*
    ;

unaryExpr
    : (NOT | SUB) unaryExpr
    | postfixExpr
    ;

postfixExpr
    : primary postfixOp*
    ;

postfixOp
    : DOT ID
    | LBRACK expr RBRACK
    | LPAREN argList? RPAREN
    ;

argList
    : expr (COMMA expr)*
    ;

primary
    : LPAREN expr RPAREN
    | INT_LIT
    | FLOAT_LIT
    | STRING_LIT
    | TRUE
    | FALSE
    | arrayLit
    | structInit
    | ID
    ;

arrayLit
    : LBRACK (expr (COMMA expr)*)? RBRACK
    ;

structInit
    : ID LBRACE fieldInit (COMMA fieldInit)* RBRACE
    ;

fieldInit
    : ID COLON expr
    ;

// ================================
// Lexer Rules
// ================================
// --------------------------------
// Keywords
// --------------------------------
LET             : 'let';
MUT             : 'mut';
FN              : 'fn';
STRUCT          : 'struct';
IF              : 'if';
ELSE            : 'else';
WHILE           : 'while';
FOR             : 'for';
IN              : 'in';
BREAK           : 'break';
CONTINUE        : 'continue';
SWITCH          : 'switch';
CASE            : 'case';
DEFAULT         : 'default';
RETURN          : 'return';
I32             : 'i32';
F32             : 'f32';
BOOL            : 'bool';
VOID            : 'void';
STRING          : 'string';
TRUE            : 'true';
FALSE           : 'false';

// --------------------------------
// OPERATORS & PUNCTUATORS
// --------------------------------
ARROW           : '->';
RANGE           : '..';

EQ              : '==';
NEQ             : '!=';
LEQ             : '<=';
GEQ             : '>=';
AND             : '&&';
OR              : '||';

LT              : '<';
GT              : '>';
NOT             : '!';
ASSIGN          : '=';

ADD             : '+';
SUB             : '-';
MUL             : '*';
DIV             : '/';
MOD             : '%';

SEMI            : ';';
COMMA           : ',';
COLON           : ':';
DOT             : '.';

LPAREN          : '(';
RPAREN          : ')';
LBRACE          : '{';
RBRACE          : '}';
LBRACK          : '[';
RBRACK          : ']';

// --------------------------------
// LITERALS
// --------------------------------
fragment Digits : [0-9]+;
fragment Exp    : [eE] [+-]? Digits;
fragment Esc    : '\\' ('n' | 't' | '"' | '\\');

INT_LIT         : Digits;
FLOAT_LIT       : Digits '.' Digits Exp? | Digits Exp;
STRING_LIT      : '"' (Esc | ~["\\\r\n])* '"'
                  {
                    s = self.text[1:-1]
                    s = s.replace("\\n", "\n")
                    s = s.replace("\\t", "\t")
                    s = s.replace('\\"', '"')
                    s = s.replace("\\\\", "\\")
                    self.text = s
                  }
                ;

// --------------------------------
// IDENTIFIER
// --------------------------------
ID              : [a-zA-Z_][a-zA-Z0-9_]*;

// --------------------------------
// COMMENTS & WHITESPACE
// --------------------------------
CMT_LINE        : '//' ~[\r\n]* -> skip;
CMT_BLOCK       : '/*' .*? '*/' -> skip;
WS              : [ \t\r\n]+ -> skip;

// --------------------------------
// LEXICAL ERROR
// --------------------------------
UNCLOSE_STRING  : '"' (Esc | ~["\\\r\n])* '\\'? (EOF | '\r'? '\n' | '\r')
                  {
                    content = self.text[1:];
                    if (content.endswith('\r\n')):
                      content = content[:-2]
                    elif (content.endswith('\n') or content.endswith('\r')):
                      content = content[:-1]
                    raise UncloseString(content)
                  }
                ;

ILLEGAL_ESCAPE  : '"' (Esc | ~["\\\r\n])* '\\' ~[nt"\\]
                  { raise IllegalEscape(self.text[1:]) }
                ;

ERROR_TOKEN     : .
                  { raise ErrorToken(self.text) }
                ;
