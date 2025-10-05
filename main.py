import sys
from lexer import lex
from parser import Parser
from interpreter import Interpreter
from codegen import CodeGen
from ast_nodes import VarDecl, Number, PrintStmt, BinOp, Var  # import all necessary AST nodes

def run_file(path, mode):
    with open(path) as f:
        code = f.read()

    # Lexical analysis
    tokens = lex(code)
    
    # Parse tokens into AST
    parser = Parser(tokens)
    tree = parser.parse()

    if mode == "interpret":
        # Directly run interpreter
        Interpreter(tree).run()
    elif mode == "compile":
        # Generate LLVM IR
        cg = CodeGen()
        cg.generate(tree)
        print("=== LLVM IR ===")
        print(cg.module)
        print("=== Program Output ===")
        try:
            # Try JIT
            cg.run_jit()
        except Exception as e:
            # Fallback to interpreter if JIT fails
            print("[Warning] LLVM JIT failed:", e)
            print("[Info] Falling back to interpreter mode...")
            Interpreter(tree).run()
    else:
        print("Unknown mode. Use 'interpret' or 'compile'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <interpret|compile> <file>")
        sys.exit(1)
    
    mode = sys.argv[1]
    filepath = sys.argv[2]
    run_file(filepath, mode)
