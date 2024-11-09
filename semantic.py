class SemanticError(Exception):
    """Exception for semantic errors encountered during analysis."""
    pass

class SymbolTable:
    """Symbol table to track declared identifiers."""
    def __init__(self):
        self.symbols = {}

    def declare(self, name):
        if name in self.symbols:
            raise SemanticError(f"Variable '{name}' is already declared.")
        self.symbols[name] = None  # Store name with no specific type tracking

    def lookup(self, name):
        if name not in self.symbols:
            raise SemanticError(f"Variable '{name}' is undeclared.")
        return self.symbols[name]

class SemanticAnalyzer:
    """Semantic Analyzer to traverse AST and validate rules."""
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()
        self.errors = []

    def analyze(self):
        """Start semantic analysis on the AST."""
        self.visit(self.ast)

        if self.errors:
            print("\nSemantic Analysis Errors:")
            for error in self.errors:
                print(error)
        else:
            print("\nSemantic Analysis Passed Successfully!")

    def visit(self, node):
        """Recursive node visit for semantic checking."""
        method_name = f"visit_{node.node_type.lower()}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

    def visit_program(self, node):
        for child in node.children:
            self.visit(child)

    def visit_assign(self, node):
        # Ensure the right-side identifier (target) is declared
        identifier_node = node.children[0]
        expr_node = node.children[1]

        # Declares right-side identifier if first-time assignment
        if identifier_node.node_type == "IDENTIFIER":
            try:
                self.symbol_table.declare(identifier_node.value)
            except SemanticError as e:
                self.errors.append(str(e))

        self.visit(expr_node)

    def visit_expr(self, node):
        # Ensure identifiers in expressions are declared
        for child in node.children:
            if child.node_type == "IDENTIFIER":
                try:
                    self.symbol_table.lookup(child.value)
                except SemanticError as e:
                    self.errors.append(str(e))
            else:
                self.visit(child)

    def visit_if(self, node):
        condition_node = node.children[0]
        if_body = node.children[1]

        self.visit(condition_node)
        self.visit(if_body)

        # Check for ELSE clause
        if len(node.children) > 2:
            else_body = node.children[2]
            self.visit(else_body)

    def visit_while(self, node):
        condition_node = node.children[0]
        body = node.children[1]

        self.visit(condition_node)
        self.visit(body)

    def visit_print(self, node):
        expr_node = node.children[0]
        self.visit(expr_node)

    def visit_identifier(self, node):
        # Ensure identifier is declared before usage
        try:
            self.symbol_table.lookup(node.value)
        except SemanticError as e:
            self.errors.append(str(e))
    def execute(self):
        """Execute the AST after successful semantic analysis."""
        if not self.errors:  # Only execute if there are no errors
            self.visit_execute(self.ast)

    def visit_execute(self, node):
        """Recursive node visit for executing statements."""
        method_name = f"execute_{node.node_type.lower()}"
        executor = getattr(self, method_name, self.generic_execute)
        return executor(node)

    def generic_execute(self, node):
        for child in node.children:
            self.visit_execute(child)

    def execute_print(self, node):
        expr_node = node.children[0]
        value = self.evaluate_expression(expr_node)
        print(value)  # Call the pout function to print the value

    def evaluate_expression(self, expr_node):
        """Evaluate expressions and return their values."""
        if expr_node.node_type == "NUMBER":
            return expr_node.value
        elif expr_node.node_type == "IDENTIFIER":
            return self.symbol_table.lookup(expr_node.value)