import os
import lexical
from parser import Parser
from semantic import SemanticAnalyzer

def process_code(code, file_name):
    """Process MiniLang code from a string, tokenize, parse, and analyze it."""
    print(f"\n{'='*50}")
    print(f"Running test case: {file_name}")
    print(f"{'='*50}")
    print("Input code: \n")
    print(code)
    
    # Tokenize the input code
    tokens = lexical.tokenize(code)

    # Parse the tokens and generate AST
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print("\nSyntax Analysis: PASSED")

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

        # Perform semantic analysis and execute if successful
        semantic_analyzer = SemanticAnalyzer(ast)
        if semantic_analyzer.analyze():
            print("\nExecution Output:")
            print("-" * 20)
            semantic_analyzer.execute()  # Execute and print output
            print("-" * 20)

    except Exception as e:
        print(f"\nError in {file_name}: {str(e)}")

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
