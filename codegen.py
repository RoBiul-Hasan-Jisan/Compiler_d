from llvmlite import ir, binding
from ast_nodes import VarDecl, Number, PrintStmt, BinOp, Var

# LLVM initialization is automatic now; no need for binding.initialize()

class CodeGen:
    def __init__(self):
        self.module = ir.Module(name="my_module")
        self.builder = None
        self.func = None
        self.symbols = {}
        self.tree = None  # store AST for interpreter fallback

    def generate(self, tree):
        self.tree = tree  # store AST
        # define main function
        func_type = ir.FunctionType(ir.IntType(32), ())
        self.func = ir.Function(self.module, func_type, name="main")
        block = self.func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        # compile main body
        main_func = next(f for f in tree.funcs if f.name == 'main')
        self.codegen_block(main_func.body)
        self.builder.ret(ir.Constant(ir.IntType(32), 0))

    def codegen_block(self, block):
        for stmt in block.statements:
            self.codegen_stmt(stmt)

    def codegen_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            val = self.codegen_expr(stmt.expr)
            ptr = self.builder.alloca(ir.IntType(32), name=stmt.name)
            self.builder.store(val, ptr)
            self.symbols[stmt.name] = ptr
        elif isinstance(stmt, PrintStmt):
            val = self.codegen_expr(stmt.expr)
            self.printf_int(val)

    def codegen_expr(self, expr):
        if isinstance(expr, Number):
            return ir.Constant(ir.IntType(32), expr.value)
        if isinstance(expr, Var):
            ptr = self.symbols[expr.name]
            return self.builder.load(ptr, expr.name)
        if isinstance(expr, BinOp):
            l = self.codegen_expr(expr.left)
            r = self.codegen_expr(expr.right)
            if expr.op == 'PLUS': 
                return self.builder.add(l, r)
            else: 
                return self.builder.sub(l, r)

    def printf_int(self, val):
        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        printf = self.module.globals.get('printf')
        if printf is None:
            printf = ir.Function(self.module, printf_ty, name="printf")

        fmt = "%d\n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_ptr = self.builder.bitcast(global_fmt, voidptr_ty)
        self.builder.call(printf, [fmt_ptr, val])

    def run_jit(self):
        import ctypes
        llvm_ir = str(self.module)

        try:
            # Try JIT compilation
            triple = binding.get_default_triple()
            target = binding.Target.from_triple(triple)
            target_machine = target.create_target_machine()
            backing_mod = binding.parse_assembly(llvm_ir)
            engine = binding.create_mcjit_compiler(backing_mod, target_machine)
            engine.finalize_object()
            func_ptr = engine.get_function_address("main")

            cfunc = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)
            return cfunc()

        except RuntimeError as e:
            # Fallback to interpreter if JIT fails
            print("[Warning] LLVM JIT failed:", e)
            print("[Info] Falling back to interpreter mode...")
            from interpreter import Interpreter
            Interpreter(self.tree).run()
