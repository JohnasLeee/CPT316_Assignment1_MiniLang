import lexical

# Example code for testing
code = """5 = x;
🔥Comment line 
x * 3 = y;
if (y > 40) {
    pout(y);
} 
else {
    pout(x);
}
"""

tokens = lexical.tokenize(code, verbose=False) # verbose is for debugging, default value = True

# usage
for token in tokens:
    print(f'Token Type: {token.token_type:<13} Value: {token.value}')