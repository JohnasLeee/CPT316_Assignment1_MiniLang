# parser.py
from lexical import Token

class ASTNode:
    """A node in the abstract syntax tree (AST) for MiniLang."""
    def __init__(self, node_type, value=None):
        self.node_type = node_type  # e.g., 'ASSIGN', 'EXPR', 'IF', 'WHILE'
        self.value = value  # e.g., variable name, operator
        self.children = []  # child nodes of this AST node

    def add_child(self, child):
        self.children.append(child)

class Parser:
    """Parser for MiniLang to generate AST and handle syntax errors."""
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def advance(self):
        """Move to the next token."""
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = Token('EOF', 0, 0)  # End of file token

    def parse(self):
        """Entry point for parsing, builds the AST."""
        ast = ASTNode("PROGRAM")
        while self.current_token.token_type != 'EOF':
            statement = self.parse_statement()
            if statement:
                ast.add_child(statement)
        return ast

    def parse_statement(self):
        """Parse individual statements like assignment, if-else, while, print."""
        if self.current_token.token_type in ('IDENTIFIER', 'NUMBER'):
            return self.parse_assignment()
        elif self.current_token.token_type == 'IF':
            return self.parse_if_statement()
        elif self.current_token.token_type == 'WHILE':
            return self.parse_while_statement()
        elif self.current_token.token_type == 'POUT':
            return self.parse_print_statement()
        else:
            self.syntax_error(f"Unexpected token ({self.current_token.value})")

    def parse_assignment(self):
        """Parse assignment statement with right-assignment format."""
        # Store the line number of the start of the assignment
        start_line = self.current_token.line
        
        # Parse the left side as an expression
        expr = self.parse_expression()

        # Expect the '=' operator for assignment
        self.expect('ASSIGN')

        # Expect an identifier on the right side of '='
        if self.current_token.token_type == 'IDENTIFIER':
            identifier_node = ASTNode("IDENTIFIER", self.current_token.value)
            self.advance()  # Move past the identifier
        else:
            self.syntax_error("Expected an identifier on the right side of '='")

        # Create an assignment node with identifier and expression
        assign_node = ASTNode("ASSIGN", "=")
        assign_node.add_child(identifier_node)  # Right side (target of assignment)
        assign_node.add_child(expr)             # Left side (value being assigned)

        # Check for semicolon and use the line number from before the semicolon
        if self.current_token.token_type != 'SEMICOLON':
            self.syntax_error_at_line("Expected SEMICOLON after Statement", start_line)
        self.advance()  # Move past the semicolon

        return assign_node

    def parse_expression(self):
        """Parse arithmetic expressions with operators +, -, *, /."""
        left = self.parse_term()
        while self.current_token.token_type in ('PLUS', 'MINUS','EQUALS', 'NOT_EQUALS', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL'):
            op = self.current_token
            self.advance()
            right = self.parse_term()
            expr_node = ASTNode("EXPR", op.value)
            expr_node.add_child(left)
            expr_node.add_child(right)
            left = expr_node  # Build expression as left-associative
        return left

    def parse_term(self):
        """Parse term in an expression, handling operators *, /."""
        left = self.parse_factor()
        while self.current_token.token_type in ('MULTIPLY', 'DIVIDE'):
            op = self.current_token
            self.advance()
            right = self.parse_factor()
            term_node = ASTNode("EXPR", op.value)
            term_node.add_child(left)
            term_node.add_child(right)
            left = term_node  # Build term as left-associative
        return left

    def parse_factor(self):
        """Parse factors: identifiers, numbers, or parenthesized expressions."""
        if self.current_token.token_type == 'NUMBER':
            number_node = ASTNode("NUMBER", self.current_token.value)
            self.advance()
            return number_node
        elif self.current_token.token_type == 'IDENTIFIER':
            identifier_node = ASTNode("IDENTIFIER", self.current_token.value)
            self.advance()
            return identifier_node
        elif self.current_token.token_type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        else:
            self.syntax_error("Expected a number, identifier, or expression")

    def parse_if_statement(self):
        """Parse if-else statement with correct ELSE level."""
        if_node = ASTNode("IF")
        self.advance()  # Consume 'if'
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        self.expect('LBRACE')
        if_body = self.parse_statement_list()
        self.expect('RBRACE')

        # Attach the condition and 'if' body to the IF node
        if_node.add_child(condition)
        if_node.add_child(if_body)

        # Check for 'else' clause and add it as a sibling node
        if self.current_token.token_type == 'ELSE':
            self.advance()
            self.expect('LBRACE')
            else_body = self.parse_statement_list()
            self.expect('RBRACE')
            
            # Create an ELSE node and add the else_body as its child
            else_node = ASTNode("ELSE")
            else_node.add_child(else_body)
            if_node.add_child(else_node)  # Add ELSE as a direct child of IF

        return if_node

    def parse_while_statement(self):
        """Parse while statement."""
        while_node = ASTNode("WHILE")
        self.advance()  # Consume 'while'
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        self.expect('LBRACE')
        body = self.parse_statement_list()
        self.expect('RBRACE')
        
        while_node.add_child(condition)
        while_node.add_child(body)
        
        return while_node

    def parse_print_statement(self):
        """Parse print statement."""
        self.advance()  # Consume 'pout'
        self.expect('LPAREN')
        expr = self.parse_expression()
        self.expect('RPAREN')
        self.expect('SEMICOLON')
        print_node = ASTNode("PRINT")
        print_node.add_child(expr)
        return print_node

    def parse_statement_list(self):
        """Parse a list of statements and encapsulate in a BLOCK node."""
        block_node = ASTNode("BLOCK")
        while self.current_token.token_type not in ('RBRACE', 'EOF'):
            stmt = self.parse_statement()
            if stmt:
                block_node.add_child(stmt)
        return block_node

    def expect(self, token_type):
        """Assert the current token is of a certain type and advance."""
        if self.current_token.token_type == token_type:
            self.advance()
        else:
            # Map token types to more descriptive error messages
            error_messages = {
                'SEMICOLON': 'Expected SEMICOLON after Statement',
                'LPAREN': 'Expected ( after Statement',
                'RPAREN': 'Expected ) after Expression',
                'LBRACE': 'Expected { after Condition',
                'RBRACE': 'Expected } after Block',
                'ASSIGN': 'Expected = in Assignment Statement'
            }
            # Use mapped message or default to token type if not mapped
            message = error_messages.get(token_type, f"Expected {token_type}")
            self.syntax_error(message)

    def syntax_error(self, message):
        """Handle syntax errors."""
        print("\nSyntax Analysis: FAILED")
        line = self.current_token.line
        print(f"Syntax Error at line {line}: {message}")
        raise Exception("Syntax error encountered")

    def syntax_error_at_line(self, message, line):
        """Handle syntax errors with a specific line number."""
        print("\nSyntax Analysis: FAILED")
        print(f"Syntax Error at line {line}: {message}")
        raise Exception("Syntax error encountered")

