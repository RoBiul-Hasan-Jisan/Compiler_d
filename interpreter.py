from ast_nodes import *

class Interpreter:
    def __init__(self, tree):
        self.tree = tree
        self.env = {}  

    def run(self):
        for func in self.tree.funcs:
            if func.name == 'main':
                self.exec_block(func.body)

    # ---------------- Block ----------------
    def exec_block(self, block):
        for stmt in block.statements:
            self.exec_stmt(stmt)

    # ---------------- Statements ----------------
    def exec_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            if stmt.dimensions:  # array
                self.env[stmt.name] = self.create_array(stmt.dimensions)
            else:
                self.env[stmt.name] = self.eval_expr(stmt.expr)

        elif isinstance(stmt, AssignStmt):
            if hasattr(stmt, 'index_exprs') and stmt.index_exprs:
                arr = self.env[stmt.name]
                idx = [self.eval_expr(e) for e in stmt.index_exprs]
                self.assign_array(arr, idx, self.eval_expr(stmt.expr))
            else:
                self.env[stmt.name] = self.eval_expr(stmt.expr)

        elif isinstance(stmt, PrintStmt):
            print(self.eval_expr(stmt.expr))

        elif isinstance(stmt, IfStmt):
            if self.eval_expr(stmt.cond):
                self.exec_block(stmt.then_block)
            elif stmt.else_block:
                self.exec_block(stmt.else_block)

        elif isinstance(stmt, WhileStmt):
            while self.eval_expr(stmt.cond):
                self.exec_block(stmt.body)

        elif isinstance(stmt, ForStmt):
            self.exec_stmt(stmt.init)
            while self.eval_expr(stmt.cond):
                self.exec_block(stmt.body)
                self.exec_stmt(stmt.update)

        elif isinstance(stmt, ReturnStmt):
            # ignoring return values for now
            pass

        else:
            raise RuntimeError(f'Unknown statement: {stmt}')

    # ---------------- Expressions ----------------
    def eval_expr(self, expr):
        if isinstance(expr, Number):
            return expr.value

        elif isinstance(expr, String):
            return expr.value

        elif isinstance(expr, Var):
            val = self.env[expr.name]
            if getattr(expr, 'index_exprs', None):
                for i in expr.index_exprs:
                    val = val[self.eval_expr(i)]
            return val

        elif isinstance(expr, ArrayAccess):
            val = self.env[expr.name]
            for i in expr.index_exprs:
                val = val[self.eval_expr(i)]
            return val

        elif isinstance(expr, Slice):
            arr = self.env[expr.var]
            start = self.eval_expr(expr.start) if expr.start else None
            end = self.eval_expr(expr.end) if expr.end else None
            return arr[start:end]

        elif isinstance(expr, BinOp):
            l = self.eval_expr(expr.left)
            r = self.eval_expr(expr.right)
            return self.eval_binop(expr.op, l, r)

        elif isinstance(expr, UnaryOp):
            val = self.eval_expr(expr.expr)
            if expr.op == 'NEG': return -val
            elif expr.op == 'NOT': return int(not val)

        else:
            raise RuntimeError(f'Unknown expression: {expr}')

    # ---------------- Operators ----------------
    def eval_binop(self, op, l, r):
        if op == 'PLUS': return l + r
        elif op == 'MINUS': return l - r
        elif op == 'MUL': return l * r
        elif op == 'DIV': return l // r
        elif op == 'MOD': return l % r
        elif op == 'LT': return int(l < r)
        elif op == 'GT': return int(l > r)
        elif op == 'LE': return int(l <= r)
        elif op == 'GE': return int(l >= r)
        elif op == 'EQ': return int(l == r)
        elif op == 'NE': return int(l != r)
        elif op == 'AND': return int(l and r)
        elif op == 'OR': return int(l or r)
        else:
            raise RuntimeError(f'Unknown operator: {op}')

    # ---------------- Arrays ----------------
    def create_array(self, dimensions):
        if len(dimensions) == 0: return 0
        dim = self.eval_expr(dimensions[0])
        return [self.create_array(dimensions[1:]) for _ in range(dim)]

    def assign_array(self, arr, indices, value):
        for idx in indices[:-1]:
            arr = arr[idx]
        arr[indices[-1]] = value
