from lexer import lex
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, type_):
        tok = self.current()
        if not tok or tok.type != type_:
            raise SyntaxError(f'Expected {type_}, got {tok}')
        self.pos += 1
        return tok

    def parse(self):
        funcs = []
        while self.current():
            funcs.append(self.parse_func())
        return Program(funcs)

    def parse_func(self):
        self.eat('FUNC')
        name = self.eat('ID').value
        self.eat('LPAREN')
        self.eat('RPAREN')
        body = self.parse_block()
        return FuncDef(name, body)

    def parse_block(self):
        self.eat('LBRACE')
        stmts = []
        while self.current() and self.current().type != 'RBRACE':
            stmts.append(self.parse_statement())
        self.eat('RBRACE')
        return Block(stmts)

    def parse_statement(self):
        tok = self.current()
        if tok.type == 'VAR':
            self.eat('VAR')
            name = self.eat('ID').value
            self.eat('ASSIGN')
            expr = self.parse_expr()
            self.eat('SEMI')
            return VarDecl(name, expr)
        elif tok.type == 'PRINT':
            self.eat('PRINT')
            self.eat('LPAREN')
            expr = self.parse_expr()
            self.eat('RPAREN')
            self.eat('SEMI')
            return PrintStmt(expr)
        else:
            raise SyntaxError(f'Unknown statement: {tok}')

    # + - lowest
    def parse_expr(self):
        left = self.parse_term()
        while self.current() and self.current().type in ('PLUS','MINUS'):
            op = self.current().type
            self.eat(op)
            right = self.parse_term()
            left = BinOp(left, op, right)
        return left

    # * / higher
    def parse_term(self):
        left = self.parse_factor()
        while self.current() and self.current().type in ('MUL','DIV'):
            op = self.current().type
            self.eat(op)
            right = self.parse_factor()
            left = BinOp(left, op, right)
        return left

    # numbers, vars, parentheses
    def parse_factor(self):
        tok = self.current()
        if tok.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(tok.value)
        elif tok.type == 'ID':
            name = self.eat('ID').value
            return Var(name)
        elif tok.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expr()
            self.eat('RPAREN')
            return expr
        else:
            raise SyntaxError(f'Unexpected token in factor: {tok}')
