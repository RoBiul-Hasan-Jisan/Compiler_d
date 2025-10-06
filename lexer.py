import re

TOKEN_SPEC = [
    # Comments
    ('COMMENT', r'//[^\n]*'),
    ('MCOMMENT', r'/\*.*?\*/'),

    # Keywords
    ('FUNC', r'func'),
    ('VAR', r'var'),
    ('PRINT', r'print'),
    ('RETURN', r'return'),
    ('IF', r'if'),
    ('ELSE', r'else'),
    ('WHILE', r'while'),
    ('FOR', r'for'),
    ('ID', r'[A-Za-z_][A-Za-z0-9_]*'),

    # Numbers
    ('NUMBER', r'\d+'),

    # Strings (double quotes)
    ('STRING', r'"(\\.|[^"\\])*"'),

    # Operators
    ('LE', r'<='), 
    ('GE', r'>='), 
    ('EQ', r'=='), 
    ('NE', r'!='), 
    ('LT', r'<'), 
    ('GT', r'>'),
    ('PLUS', r'\+'), 
    ('MINUS', r'-'), 
    ('MUL', r'\*'), 
    ('DIV', r'/'), 
    ('MOD', r'%'),
    ('AND', r'&&'), 
    ('OR', r'\|\|'), 
    ('NOT', r'!'),
    ('INC', r'\+\+'), 
    ('DEC', r'--'),
    ('ASSIGN', r'='),

    # Delimiters
    ('LBRACE', r'\{'), 
    ('RBRACE', r'\}'),
    ('LPAREN', r'\('), 
    ('RPAREN', r'\)'),
    ('LBRACKET', r'\['), 
    ('RBRACKET', r'\]'),
    ('SEMI', r';'),
    ('COMMA', r','), 
    ('COLON', r':'),

    # Whitespace
    ('SKIP', r'[ \t\n]+'),

    # Any other character
    ('MISMATCH', r'.'),
]

TOK_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f'Token({self.type},{self.value})'

def lex(code):
    for mo in re.finditer(TOK_REGEX, code, re.DOTALL):
        kind, value = mo.lastgroup, mo.group()
        if kind == 'NUMBER':
            yield Token('NUMBER', int(value))
        elif kind == 'STRING':
            value = value[1:-1]  # remove quotes
            yield Token('STRING', value)
        elif kind in ('SKIP', 'COMMENT', 'MCOMMENT'):
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value}')
        else:
            yield Token(kind, value)

