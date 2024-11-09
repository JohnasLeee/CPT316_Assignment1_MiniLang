import os
import lexical
from parser import Parser
from semantic import SemanticAnalyzer

def process_code(code, file_name):
    """Process MiniLang code from a string, tokenize, parse, and analyze it."""
    print(f"\nRunning test case: {file_name}")
    print(code)
    
    # Tokenize the input code
    tokens = lexical.tokenize(code, verbose=False)
    print("Tokens:")
    for token in tokens:
        print(f'Token Type: {token.token_type:<13} Value: {token.value}')
    print("\n")

    # Parse the tokens and generate AST
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print("AST Generated Successfully:")

        def display_simple_ast(node, prefix=""):
            """Display a simple ASCII representation of the AST."""
            if node.value is not None:
                node_label = f"{node.node_type} ({node.value})"
            else:
                node_label = node.node_type
            print(prefix + node_label)
            if node.children:
                for child in node.children:
                    display_simple_ast(child, prefix + "   |-- ")

        display_simple_ast(ast)

        # Perform semantic analysis on the AST
        semantic_analyzer = SemanticAnalyzer(ast)
        if semantic_analyzer.analyze():
            semantic_analyzer.execute()

    except Exception as e:
        print(f"Error in {file_name}: {str(e)}")

def main():
    # Path to the test cases folder
    test_cases_folder = os.path.join(os.path.dirname(__file__), "Test_cases")

    # Iterate over each file in the test cases folder
    for file_name in os.listdir(test_cases_folder):
        file_path = os.path.join(test_cases_folder, file_name)
        with open(file_path, 'r') as file:
            code = file.read()
            process_code(code, file_name)

if __name__ == "__main__":
    main()
