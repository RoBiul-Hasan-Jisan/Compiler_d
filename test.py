from lexer import lex
from parser import Parser

# Minimal 1D array test code
source_code = """
// Declare a 1D array
var arr[5];

// Assign values
arr[0] = 10;
arr[1] = 20;
arr[2] = 30;
arr[3] = 40;
arr[4] = 50;

// Print values
print(arr[0]);
print(arr[1]);
print(arr[2]);
print(arr[3]);
print(arr[4]);

// Use in expressions
var sum;
sum = arr[0] + arr[1] + arr[2] + arr[3] + arr[4];
print(sum);

"""

# Lexing
tokens = [tok for tok in lex(source_code) if tok is not None]

# Debug: print all tokens
for i, tok in enumerate(tokens):
    print(i, tok, getattr(tok, 'type', None))

# Parsing
parser = Parser(tokens)
ast = parser.parse()

print("Parsing succeeded!")
print(ast)
