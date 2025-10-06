from ast_nodes import *
from lexer import lex

class Parser:
    def __init__(self, tokens):
        # filter out any None tokens from lexer
        self.tokens = [tok for tok in tokens if tok is not None]
        self.pos = 0

    # safely get current token
    def current(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos] is None:
            self.pos += 1
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    # consume a token of expected type
    def eat(self, type_):
        tok = self.current()
        if not tok:
            raise SyntaxError(f'Unexpected end of input, expected {type_}')
        if tok.type != type_:
            raise SyntaxError(f'Expected {type_}, got {tok}')
        self.pos += 1
        return tok

    # ---------------- Program ----------------
    def parse(self):
        stmts = []
        while self.current():
            tok = self.current()
            if tok.type == 'FUNC':
                stmts.append(self.parse_func())
            else:
                stmt = self.parse_statement()
                if stmt:
                    stmts.append(stmt)
        return Program(stmts)

    # ---------------- Functions ----------------
    def parse_func(self):
        self.eat('FUNC')
        name = self.eat('ID').value
        self.eat('LPAREN')
        self.eat('RPAREN')
        body = self.parse_block()
        return FuncDef(name, body)

    # ---------------- Blocks ----------------
    def parse_block(self):
        tok = self.current()
        if not tok:
            raise SyntaxError("Unexpected end of input, expected block start")

        if tok.type == 'LBRACE':
            start, end = 'LBRACE', 'RBRACE'
        elif tok.type == 'LT':
            start, end = 'LT', 'GT'
        else:
            raise SyntaxError(f'Expected block start, got {tok}')

        self.eat(start)
        stmts = []

        while True:
            tok = self.current()
            if tok is None:
                raise SyntaxError(f"Unexpected end of input inside block, expected {end}")
            if tok.type == end:
                break
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)

        self.eat(end)
        return Block(stmts)

    # ---------------- Statements ----------------
    def parse_statement(self):
        tok = self.current()
        if not tok:
            return None

        if tok.type in ('LBRACE', 'LT'):
            return self.parse_block()

        if tok.type == 'VAR':
            return self.parse_var_decl()

        if tok.type == 'ID':
            return self.parse_assignment_or_var()

        if tok.type == 'PRINT':
            return self.parse_print()

        if tok.type == 'IF':
            return self.parse_if()

        if tok.type == 'WHILE':
            return self.parse_while()

        if tok.type == 'FOR':
            return self.parse_for()

        if tok.type == 'RETURN':
            return self.parse_return()

        # otherwise treat as expression statement
        expr = self.parse_expr()
        if self.current() and self.current().type == 'SEMI':
            self.eat('SEMI')
        return ExprStmt(expr)

    # ---------------- Variable Declaration ----------------
    def parse_var_decl(self):
        self.eat('VAR')
        name = self.eat('ID').value
        dimensions = []
        while self.current() and self.current().type == 'LBRACKET':
            self.eat('LBRACKET')
            dimensions.append(self.parse_expr())
            self.eat('RBRACKET')
        expr = None
        if self.current() and self.current().type == 'ASSIGN':
            self.eat('ASSIGN')
            expr = self.parse_expr()
        if self.current() and self.current().type == 'SEMI':
            self.eat('SEMI')
        return VarDecl(name, expr, dimensions or None)

    # ---------------- Assignment / Variable ----------------
    def parse_assignment_or_var(self):
        name = self.eat('ID').value
        index_exprs = []
        while self.current() and self.current().type == 'LBRACKET':
            self.eat('LBRACKET')
            index_exprs.append(self.parse_expr())
            self.eat('RBRACKET')
        if self.current() and self.current().type == 'ASSIGN':
            self.eat('ASSIGN')
            expr = self.parse_expr()
            if self.current() and self.current().type == 'SEMI':
                self.eat('SEMI')
            return AssignStmt(name, expr, index_exprs or None)
        else:
            if self.current() and self.current().type == 'SEMI':
                self.eat('SEMI')
            if index_exprs:
                return ArrayAccess(name, index_exprs)
            return Var(name)

    # ---------------- Print ----------------
    def parse_print(self):
        self.eat('PRINT')
        self.eat('LPAREN')
        expr = self.parse_expr()
        self.eat('RPAREN')
        self.eat('SEMI')
        return PrintStmt(expr)

    # ---------------- If / While / Return ----------------
    def parse_if(self):
        self.eat('IF')
        if self.current() and self.current().type == 'LPAREN':
            self.eat('LPAREN')
            cond = self.parse_expr()
            self.eat('RPAREN')
        else:
            cond = self.parse_expr()
        then_block = self.parse_block()
        else_block = None
        if self.current() and self.current().type == 'ELSE':
            self.eat('ELSE')
            else_block = self.parse_block()
        return IfStmt(cond, then_block, else_block)

    def parse_while(self):
        self.eat('WHILE')
        if self.current() and self.current().type == 'LPAREN':
            self.eat('LPAREN')
            cond = self.parse_expr()
            self.eat('RPAREN')
        else:
            cond = self.parse_expr()
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_return(self):
        self.eat('RETURN')
        expr = None
        if self.current() and self.current().type != 'SEMI':
            expr = self.parse_expr()
        self.eat('SEMI')
        return ReturnStmt(expr)

    # ---------------- For Loop ----------------
    def parse_simple_statement(self):
        tok = self.current()
        if not tok:
            raise SyntaxError("Unexpected end of input in for-loop")
        if tok.type == 'VAR':
            return self.parse_var_decl()
        elif tok.type == 'ID':
            return self.parse_assignment_or_var()
        else:
            raise SyntaxError(f'Invalid simple statement in for-loop: {tok}')

    def parse_for(self):
        self.eat('FOR')
        self.eat('LPAREN')
        init = self.parse_simple_statement()
        self.eat('SEMI')
        cond = self.parse_expr()
        self.eat('SEMI')
        update = self.parse_simple_statement()
        self.eat('RPAREN')
        body = self.parse_block()
        return ForStmt(init, cond, update, body)

    # ---------------- Expressions ----------------
    def parse_expr(self):
        return self.parse_logical()

    def parse_logical(self):
        left = self.parse_comparison()
        while True:
            tok = self.current()
            if tok and tok.type in ('AND', 'OR'):
                op = tok.type
                self.eat(op)
                right = self.parse_comparison()
                left = BinOp(left, op, right)
            else:
                break
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while True:
            tok = self.current()
            if tok and tok.type in ('GT','LT','GE','LE','EQ','NE'):
                op = tok.type
                self.eat(op)
                right = self.parse_term()
                left = BinOp(left, op, right)
            else:
                break
        return left

    def parse_term(self):
        left = self.parse_factor()
        while True:
            tok = self.current()
            if tok and tok.type in ('PLUS','MINUS'):
                op = tok.type
                self.eat(op)
                right = self.parse_factor()
                left = BinOp(left, op, right)
            else:
                break
        return left

    def parse_factor(self):
        tok = self.current()
        if not tok:
            raise SyntaxError("Unexpected end of input in factor")

        # Unary minus
        if tok.type == 'MINUS':
            self.eat('MINUS')
            return UnaryOp('NEG', self.parse_factor())

        left = self.parse_atom()
        while True:
            tok = self.current()
            if tok and tok.type in ('MUL','DIV','MOD'):
                op = tok.type
                self.eat(op)
                right = self.parse_atom()
                left = BinOp(left, op, right)
            else:
                break
        return left

    def parse_atom(self):
        tok = self.current()
        if not tok:
            raise SyntaxError("Unexpected end of input in atom")

        if tok.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(tok.value)
        elif tok.type == 'STRING':
            self.eat('STRING')
            return String(tok.value)
        elif tok.type == 'ID':
            name = self.eat('ID').value
            index_exprs = []
            while self.current() and self.current().type == 'LBRACKET':
                self.eat('LBRACKET')
                index_exprs.append(self.parse_expr())
                self.eat('RBRACKET')
            if index_exprs:
                return ArrayAccess(name, index_exprs)
            return Var(name)
        elif tok.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expr()
            self.eat('RPAREN')
            return expr
        else:
            raise SyntaxError(f'Unexpected token: {tok}')

# ---------------- AST Node for Expression Statements ----------------
class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr
