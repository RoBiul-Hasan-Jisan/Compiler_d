import re

TOKEN_SPEC = [
    ('NUMBER',   r'\d+'),
    ('FUNC',     r'func'),
    ('VAR',      r'var'),
    ('PRINT',    r'print'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('SEMI',     r';'),
    ('ASSIGN',   r'='),
    ('COMMENT',  r'//[^\n]*'),       # <-- move before DIV
    ('MCOMMENT', r'/\*.*?\*/'),      # <-- move before DIV
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('MUL',      r'\*'),
    ('DIV',      r'/'),               # <-- single / at the end
    ('SKIP',     r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]


TOK_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f'Token({self.type},{self.value})'

def lex(code):
    for mo in re.finditer(TOK_REGEX, code, re.DOTALL):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            yield Token('NUMBER', int(value))
        elif kind in ('SKIP', 'COMMENT', 'MCOMMENT'):
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected char {value}')
        else:
            yield Token(kind, value)
