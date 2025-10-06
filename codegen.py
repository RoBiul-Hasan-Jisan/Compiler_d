from llvmlite import ir, binding
from ast_nodes import VarDecl, Number, PrintStmt, BinOp, Var

# LLVM initialization (do once)
binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

class CodeGen:
    def __init__(self):
        self.module = ir.Module(name="my_module")
        self.builder = None
        self.func = None
        self.symbols = {}
        self.tree = None  # store AST for interpreter fallback
        self._fmt_counter = 0  # counter for unique printf format strings

    # ---------------- Generate main function ----------------
    def generate(self, tree):
        self.tree = tree  # store AST for fallback
        # define main function
        func_type = ir.FunctionType(ir.IntType(32), ())
        self.func = ir.Function(self.module, func_type, name="main")
        block = self.func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        # compile main body
        main_func = next(f for f in tree.funcs if f.name == 'main')
        self.codegen_block(main_func.body)
        self.builder.ret(ir.Constant(ir.IntType(32), 0))

    # ---------------- Generate block ----------------
    def codegen_block(self, block):
        for stmt in block.statements:
            self.codegen_stmt(stmt)

    # ---------------- Generate statement ----------------
    def codegen_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            val = self.codegen_expr(stmt.expr)
            ptr = self.builder.alloca(ir.IntType(32), name=stmt.name)
            self.builder.store(val, ptr)
            self.symbols[stmt.name] = ptr
        elif isinstance(stmt, PrintStmt):
            val = self.codegen_expr(stmt.expr)
            self.printf_int(val)

    # ---------------- Generate expression ----------------
    def codegen_expr(self, expr):
        if isinstance(expr, Number):
            return ir.Constant(ir.IntType(32), expr.value)
        if isinstance(expr, Var):
            ptr = self.symbols.get(expr.name)
            if ptr is None:
                raise RuntimeError(f"Undefined variable {expr.name} in JIT")
            return self.builder.load(ptr, expr.name)
        if isinstance(expr, BinOp):
            l = self.codegen_expr(expr.left)
            r = self.codegen_expr(expr.right)
            if expr.op == 'PLUS': 
                return self.builder.add(l, r)
            elif expr.op == 'MINUS': 
                return self.builder.sub(l, r)
            elif expr.op == 'MUL': 
                return self.builder.mul(l, r)
            elif expr.op == 'DIV': 
                return self.builder.sdiv(l, r)
            else:
                raise RuntimeError(f"Unknown operator {expr.op}")

    # ---------------- Print integer ----------------
    def printf_int(self, val):
        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        printf = self.module.globals.get('printf')
        if printf is None:
            printf = ir.Function(self.module, printf_ty, name="printf")

        fmt = "%d\n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))

        # make unique global name for each printf call
        name = f"fstr_{self._fmt_counter}"
        self._fmt_counter += 1

        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name=name)
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_ptr = self.builder.bitcast(global_fmt, voidptr_ty)
        self.builder.call(printf, [fmt_ptr, val])

    # ---------------- Run JIT ----------------
    def run_jit(self):
        import ctypes
        llvm_ir = str(self.module)

        try:
            # JIT compilation
            triple = binding.get_default_triple()
            target = binding.Target.from_triple(triple)
            target_machine = target.create_target_machine()
            backing_mod = binding.parse_assembly(llvm_ir)
            engine = binding.create_mcjit_compiler(backing_mod, target_machine)
            engine.finalize_object()
            func_ptr = engine.get_function_address("main")

            # Call the JITed function
            cfunc = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)
            return cfunc()

        except RuntimeError as e:
            # Fallback to interpreter if JIT fails
            print("[Warning] LLVM JIT failed:", e)
            print("[Info] Falling back to interpreter mode...")
            from interpreter import HybridInterpreter
            HybridInterpreter(self.tree).run()
