class Token:
    """A token in the MiniLang language."""
    def __init__(self, token_type: str, line: int, column: int, value=None):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

class LexicalError(Exception):
    """Exception raised for lexical errors in the source code."""
    pass

class Lexer:
    """Lexical analyzer for MiniLang."""
    
    KEYWORDS = {'if', 'else', 'while', 'pout'}
    OPERATORS = {
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'MULTIPLY',
        '/': 'DIVIDE',
        '=': 'ASSIGN',
        '==': 'EQUALS',
        '!=': 'NOT_EQUALS',
        '<': 'LESS_THAN',
        '>': 'GREATER_THAN',
        '<=': 'LESS_EQUAL',
        '>=': 'GREATER_EQUAL',
        '(': 'LPAREN',
        ')': 'RPAREN',
        '{': 'LBRACE',
        '}': 'RBRACE',
        ';': 'SEMICOLON',
    }

    def __init__(self, source: str):
        self.source = source
        self.line = 1
        self.column = 1
        self.current_char = None
        self.buffer = []
        self.errors = []
        self.advance()

    def error(self, message: str):
        """Log a lexical error with position information."""
        self.errors.append(f"Line {self.line}, Column {self.column-1}: {message}")

    def advance(self):
        """Read the next character from the source."""
        if self.buffer:
            self.current_char = self.buffer.pop(0)
        else:
            self.current_char = self.source.read(1)
            
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    def peek(self) -> str:
        """Look at the next character without consuming it."""
        if not self.buffer:
            char = self.source.read(1)
            if char:
                self.buffer.append(char)
            return char
        return self.buffer[0] if self.buffer else ''

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def read_number(self) -> Token:
        """Read a numeric literal."""
        result = ''
        start_column = self.column - 1
        
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char and (self.current_char.isalpha() or self.current_char == '_'):
            self.error("Identifiers cannot start with a number")
            return None

        return Token('NUMBER', self.line, start_column, int(result))

    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        result = ''
        start_column = self.column - 1
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # Check if it's a keyword
        if result in self.KEYWORDS:
            return Token(result.upper(), self.line, start_column, result)
        return Token('IDENTIFIER', self.line, start_column, result)

    def read_operator(self) -> Token:
        """Read an operator."""
        start_column = self.column - 1
        current = self.current_char
        next_char = self.peek()
        
        # Check for two-character operators
        if current + next_char in self.OPERATORS:
            op = current + next_char
            self.advance()  # Consume the second character
            self.advance()
            return Token(self.OPERATORS[op], self.line, start_column, op)
        
        # Single-character operators
        if current in self.OPERATORS:
            op = current
            self.advance()
            return Token(self.OPERATORS[op], self.line, start_column, op)
            
        self.error(f"Invalid operator: {current}")
        return None

    def skip_comment(self):
        """Skip all characters until the end of the current line."""
        while self.current_char and self.current_char != '\n':
            self.advance()
        if self.current_char:  # If we found a newline
            self.advance()

    def next_token(self) -> Token:
        """Get the next token from the source."""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                token = self.read_number()
                if token:
                    return token
                continue

            if self.current_char.isalpha():
                return self.read_identifier()

            if self.current_char in '+-*/=!<>(){};':
                token = self.read_operator()
                if token:
                    return token
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            self.error(f"Invalid character: '{self.current_char}'")
            self.advance()

        return Token('EOF', self.line, self.column, None)

def tokenize(source_code: str, verbose=True):
    """Tokenize a string of source code and collect any lexical errors."""
    from io import StringIO
    lexer = Lexer(StringIO(source_code))
    tokens = []

    
    while True:
        token = lexer.next_token()
        if token:
            tokens.append(token)
        if token and token.token_type == 'EOF':
            break
    
        # Print tokens
    if not lexer.errors:
        if verbose:
            print(f'Code:\n{source_code}')
            print(f"{'Name':<10} {'Value':<10} {'Line':<6} {'Column':<6}")
            print("-" * 32)  # Separator line
            for token in tokens:
                print(f"{token.token_type:<12} {token.value if token.value is not None else 'EOF':<10} {token.line:<6} {token.column:<6}")

        print("\nLexical Analysis: PASSED")
        return tokens

    # Print all collected errors
    else:
        print("LEXICAL ERROR")
        if verbose:
            for error in lexer.errors:
                print(error)
        return []


