# =================== AST NODES ===================
class Node: pass

# ---------------- Expressions ----------------
class Number(Node):
    def __init__(self, value): self.value = value

class Var(Node):
    def __init__(self, name, index_exprs=None):
        self.name = name
        self.index_exprs = index_exprs  # for array access

class BinOp(Node):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right

class UnaryOp(Node):
    def __init__(self, op, expr): self.op, self.expr = op, expr

# ---------------- Statements ----------------
class VarDecl(Node):
    def __init__(self, name, expr, dimensions=None):
        self.name = name
        self.expr = expr
        self.dimensions = dimensions  # for arrays

class AssignStmt(Node):
    def __init__(self, name, expr, index_exprs=None):
        self.name = name
        self.expr = expr
        self.index_exprs = index_exprs  # for array assignment

class PrintStmt(Node):
    def __init__(self, expr): self.expr = expr

class IfStmt(Node):
    def __init__(self, cond, then_block, else_block=None):
        self.cond, self.then_block, self.else_block = cond, then_block, else_block

class WhileStmt(Node):
    def __init__(self, cond, body): self.cond, self.body = cond, body

class ForStmt(Node):
    def __init__(self, init, cond, update, body): self.init, self.cond, self.update, self.body = init, cond, update, body

class ReturnStmt(Node):
    def __init__(self, expr=None): self.expr = expr

class FuncCall(Node):
    def __init__(self, name, args=None): self.name, self.args = name, args or []

# ---------------- Blocks & Functions ----------------
class Block(Node):
    def __init__(self, statements=None): self.statements = statements or []

class FuncDef(Node):
    def __init__(self, name, body): self.name, self.body = name, body

class Program(Node):
    def __init__(self, funcs): self.funcs = funcs
class ArrayAccess(Node):
    def __init__(self, name, index_exprs):
        self.name = name
        self.index_exprs = index_exprs  # list of expressions, e.g., [i, j]
class Slice(Node):
    def __init__(self, var, start=None, end=None):
        self.var = var
        self.start = start
        self.end = end
