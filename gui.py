import tkinter as tk
from tkinter import filedialog
from lexer import lex
from parser import Parser
from codegen import CodeGen
from interpreter import Interpreter as HybridInterpreter
import sys
from io import StringIO
import builtins

#from interpreter import Interpreter as HybridInterpreter


class MyCCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyCC GUI Compiler/Interpreter")
        self.root.geometry("900x700")

        # ---------------- Menu ----------------
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)

        # ---------------- Buttons ----------------
        btn_frame = tk.Frame(root)
        btn_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.run_btn = tk.Button(btn_frame, text="Run", command=self.run_code, bg="green", fg="white")
        self.run_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side="left", padx=5)

        # ---------------- Editor ----------------
        editor_frame = tk.Frame(root)
        editor_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.editor_scroll = tk.Scrollbar(editor_frame)
        self.editor_scroll.pack(side="right", fill="y")

        self.editor = tk.Text(editor_frame, wrap="none", font=("Consolas", 12),
                              yscrollcommand=self.editor_scroll.set)
        self.editor.pack(fill="both", expand=True)
        self.editor_scroll.config(command=self.editor.yview)

        # ---------------- Output Console ----------------
        output_frame = tk.Frame(root)
        output_frame.pack(fill="x", padx=5, pady=5)

        self.output_scroll = tk.Scrollbar(output_frame)
        self.output_scroll.pack(side="right", fill="y")

        self.output = tk.Text(output_frame, height=12, bg="black", fg="white",
                              yscrollcommand=self.output_scroll.set)
        self.output.pack(fill="x")
        self.output.tag_config("error", foreground="red")
        self.output_scroll.config(command=self.output.yview)

        # Captured output
        self.captured_output = ""

    # ---------------- File Open ----------------
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("MyCC files","*.my")])
        if path:
            with open(path) as f:
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, f.read())

    # ---------------- Clear Output ----------------
    def clear_output(self):
        self.output.delete("1.0", tk.END)
        self.captured_output = ""

    # ---------------- Run Code ----------------
    def run_code(self):
        code = self.editor.get("1.0", tk.END)
        self.output.delete("1.0", tk.END)
        self.captured_output = ""

        try:
            # -------- Lexer & Parser --------
            tokens = lex(code)
            parser = Parser(tokens)
            tree = parser.parse()

            # -------- LLVM CodeGen --------
            cg = CodeGen()
            cg.generate(tree)

            self.captured_output += "\n=== LLVM IR ===\n"
            self.captured_output += str(cg.module)
            self.captured_output += "\n=== Program Output ===\n"

            # -------- Capture Output via HybridInterpreter --------
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            try:
                HybridInterpreter(tree).run()
            finally:
                sys.stdout = old_stdout
            self.captured_output += mystdout.getvalue()

        except Exception as e:
            if hasattr(e, 'token') and hasattr(e.token, 'line'):
                self.captured_output += f"Error at line {e.token.line}: {str(e)}\n"
            else:
                self.captured_output += f"Error: {str(e)}\n"

        # -------- Show output in GUI console --------
        self.output.insert(tk.END, self.captured_output)

    # -------- Capture print helper (optional) --------
    def _capture_print(self, *args):
        self.captured_output += " ".join(map(str, args)) + "\n"

if __name__ == "__main__":
    root = tk.Tk()
    app = MyCCApp(root)
    root.mainloop()
