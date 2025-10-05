class Node: pass

class Number(Node):
    def __init__(self, value): self.value = value

class Var(Node):
    def __init__(self, name): self.name = name

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left, self.op, self.right = left, op, right

class VarDecl(Node):
    def __init__(self, name, expr):
        self.name, self.expr = name, expr

class PrintStmt(Node):
    def __init__(self, expr): self.expr = expr

class Block(Node):
    def __init__(self, statements): self.statements = statements

class FuncDef(Node):
    def __init__(self, name, body): self.name, self.body = name, body

class Program(Node):
    def __init__(self, funcs): self.funcs = funcs
