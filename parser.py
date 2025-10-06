from ast_nodes import *  # make sure AST nodes are defined
from lexer import lex     # your lexer producing tokens

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

    # ---------------- Program ----------------
    def parse(self):
        stmts = []
        while self.current():
            if self.current().type == 'FUNC':
                stmts.append(self.parse_func())
            else:
                stmts.append(self.parse_statement())
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
        if tok.type == 'LBRACE':
            start, end = 'LBRACE', 'RBRACE'
        elif tok.type == 'LT':
            start, end = 'LT', 'GT'
        else:
            raise SyntaxError(f'Expected block start, got {tok}')

        self.eat(start)
        stmts = []
        while self.current() and self.current().type != end:
            stmts.append(self.parse_statement())
        self.eat(end)
        return Block(stmts)

    # ---------------- Statements ----------------
    def parse_statement(self):
        tok = self.current()
        if not tok:
            return None

        # --- Block as statement ---
        if tok.type in ('LBRACE', 'LT'):
            return self.parse_block()

        # --- Variable declaration ---
        if tok.type == 'VAR':
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

        # --- Assignment or variable reference ---
        elif tok.type == 'ID':
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
                return Var(name)

        # --- Print statement ---
        elif tok.type == 'PRINT':
            self.eat('PRINT')
            self.eat('LPAREN')
            expr = self.parse_expr()
            self.eat('RPAREN')
            self.eat('SEMI')
            return PrintStmt(expr)

        # --- Control statements ---
        elif tok.type == 'IF':
            return self.parse_if()
        elif tok.type == 'WHILE':
            return self.parse_while()
        elif tok.type == 'FOR':
            return self.parse_for()
        elif tok.type == 'RETURN':
            self.eat('RETURN')
            expr = None
            if self.current() and self.current().type != 'SEMI':
                expr = self.parse_expr()
            self.eat('SEMI')
            return ReturnStmt(expr)

        # --- Expression statement (fix for bare numbers or expressions) ---
        else:
            expr = self.parse_expr()
            if self.current() and self.current().type == 'SEMI':
                self.eat('SEMI')
            return ExprStmt(expr)  # new AST node for expressions

    # ---------------- For loop helper ----------------
    def parse_simple_statement(self):
        tok = self.current()
        if tok.type == 'ID':
            name = self.eat('ID').value
            index_exprs = []
            while self.current() and self.current().type == 'LBRACKET':
                self.eat('LBRACKET')
                index_exprs.append(self.parse_expr())
                self.eat('RBRACKET')
            self.eat('ASSIGN')
            expr = self.parse_expr()
            return AssignStmt(name, expr, index_exprs or None)

        elif tok.type == 'VAR':
            self.eat('VAR')
            name = self.eat('ID').value
            expr = None
            if self.current() and self.current().type == 'ASSIGN':
                self.eat('ASSIGN')
                expr = self.parse_expr()
            return VarDecl(name, expr, None)

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

    # ---------------- If / While ----------------
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

    # ---------------- Expressions ----------------
    def parse_expr(self):
        return self.parse_logical()

    def parse_logical(self):
        left = self.parse_term()
        while self.current() and self.current().type in ('AND','OR'):
            op = self.current().type
            self.eat(op)
            right = self.parse_term()
            left = BinOp(left, op, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current() and self.current().type in ('PLUS','MINUS'):
            op = self.current().type
            self.eat(op)
            right = self.parse_factor()
            left = BinOp(left, op, right)
        return left

    def parse_factor(self):
        left = self.parse_atom()
        while self.current() and self.current().type in ('MUL','DIV','MOD'):
            op = self.current().type
            self.eat(op)
            right = self.parse_atom()
            left = BinOp(left, op, right)
        return left

    def parse_atom(self):
        tok = self.current()
        if tok.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(tok.value)
        elif tok.type == 'ID':
            name = self.eat('ID').value
            index_exprs = []
            while self.current() and self.current().type == 'LBRACKET':
                self.eat('LBRACKET')
                index_exprs.append(self.parse_expr())
                self.eat('RBRACKET')
            if index_exprs:
                return ArrayAccess(name, index_exprs)
            else:
                return Var(name)
        elif tok.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expr()
            self.eat('RPAREN')
            return expr
        else:
            raise SyntaxError(f'Unexpected token: {tok}')

# ---------------- AST Node for expression statements ----------------
class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr
