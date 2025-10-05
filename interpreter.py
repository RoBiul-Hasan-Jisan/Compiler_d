from ast_nodes import *

class Interpreter:
    def __init__(self, tree):
        self.tree = tree
        self.env = {}

    def run(self):
        for func in self.tree.funcs:
            if func.name == 'main':
                self.exec_block(func.body)

    def exec_block(self, block):
        for stmt in block.statements:
            self.exec_stmt(stmt)

    def exec_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            self.env[stmt.name] = self.eval_expr(stmt.expr)
        elif isinstance(stmt, PrintStmt):
            print(self.eval_expr(stmt.expr))
        else:
            raise RuntimeError(f'Unknown statement type: {stmt}')

    def eval_expr(self, expr):
        if isinstance(expr, Number):
            return expr.value
        elif isinstance(expr, Var):
            if expr.name not in self.env:
                raise RuntimeError(f'Undefined variable {expr.name}')
            return self.env[expr.name]
        elif isinstance(expr, BinOp):
            left = self.eval_expr(expr.left)
            right = self.eval_expr(expr.right)
            if expr.op == 'PLUS': return left + right
            elif expr.op == 'MINUS': return left - right
            elif expr.op == 'MUL': return left * right
            elif expr.op == 'DIV': return left // right   # integer division
            else:
                raise RuntimeError(f'Unknown operator {expr.op}')
        else:
            raise RuntimeError(f'Unknown expression type {expr}')
