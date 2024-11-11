import lexical
from parser import Parser
from semantic import SemanticAnalyzer

# Example code for testing
code = """5 = x;
🔥Comment line 
x * 3 + x = y;
if (y > 40) {
    if(x > 40){
        pout(x);
        if(y > 40){
            pout(y);
        }
        else{
            pout(x);
        }
    }
    pout(y);
} 
else {
    pout(x);
}
"""

tokens = lexical.tokenize(code, verbose=False)  # Tokenize the input code

# Display tokens for debugging
for token in tokens:
    print(f'Token Type: {token.token_type:<13} Value: {token.value}')

print('\n')

# Parse the tokens to generate AST
try:
    parser = Parser(tokens)
    ast = parser.parse()
    print("\nAST Generated Successfully:")
    
    def display_simple_ast(node, prefix=""):
        """Display a simple ASCII representation of the AST."""
        # Define the label with both node type and value, if the value is available
        if node.value is not None:
            node_label = f"{node.node_type} ({node.value})"
        else:
            node_label = node.node_type

        # Print the current node with its prefix
        print(prefix + node_label)

        # Use "   |-- " for children to indicate branching
        if node.children:
            for i, child in enumerate(node.children):
                child_prefix = prefix + "   |-- "
                display_simple_ast(child, child_prefix)

    # Call this function with the root AST node after parsing
    display_simple_ast(ast)

    # Perform semantic analysis on the AST
    semantic_analyzer = SemanticAnalyzer(ast)
    semantic_analyzer.analyze()

except Exception as e:
    print(str(e))
