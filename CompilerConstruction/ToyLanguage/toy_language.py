#!/usr/bin/env python3
import re
import sys

TOKEN_SPEC = [
    ('NUMBER', r'\d+(?:\.\d+)?'),
    ('STRING', r'"(?:\\.|[^\\"])*"'),
    ('IDENT', r'[A-Za-z_]\w*'),
    ('EQ', r'=='),
    ('NE', r'!='),
    ('LE', r'<=') ,
    ('GE', r'>='),
    ('LT', r'<'),
    ('GT', r'>') ,
    ('ASSIGN', r'='),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('COMMA', r','),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('MUL', r'\*'),
    ('DIV', r'/'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('SEMICOLON', r';'),
    ('MISMATCH', r'.'),
]

TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC))

class Token:
    def __init__(self, kind, value, line):
        self.kind = kind
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, line={self.line})"


def tokenize(text):
    line = 1
    pos = 0
    while pos < len(text):
        if text.startswith('#', pos):
            end = text.find('\n', pos)
            pos = len(text) if end == -1 else end
            continue
        match = TOKEN_RE.match(text, pos)
        if not match:
            raise SyntaxError(f'Unexpected character at line {line}: {text[pos]}')
        kind = match.lastgroup
        value = match.group(kind)
        pos = match.end()
        if kind == 'NEWLINE':
            line += 1
            yield Token('NEWLINE', value, line)
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected token at line {line}: {value}')
        else:
            yield Token(kind, value, line)
    yield Token('EOF', '', line)

class Parser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    @property
    def current(self):
        return self.tokens[self.pos]

    def eat(self, kind=None):
        token = self.current
        if kind and token.kind != kind:
            raise SyntaxError(f'Expected {kind} at line {token.line}, got {token.kind}')
        self.pos += 1
        return token

    def parse(self):
        statements = []
        while self.current.kind != 'EOF':
            if self.current.kind == 'NEWLINE':
                self.eat('NEWLINE')
                continue
            statements.append(self.statement())
        return statements

    def statement(self):
        if self.current.kind == 'IDENT':
            if self.current.value == 'agar':
                return self.if_statement()
            if self.current.value == 'jabtak':
                return self.while_statement()
            if self.current.value == 'chalo':
                return self.for_statement()
            if self.current.value == 'kro':
                return self.do_while_statement()

        expr = self.expression()
        if self.current.kind == 'ASSIGN' and isinstance(expr, Var):
            self.eat('ASSIGN')
            value = self.expression()
            if self.current.kind == 'SEMICOLON':
                self.eat('SEMICOLON')
            return Assign(expr.name, value)
        if self.current.kind == 'SEMICOLON':
            self.eat('SEMICOLON')
        while self.current.kind == 'NEWLINE':
            self.eat('NEWLINE')
        return ExprStmt(expr)

    def if_statement(self):
        self.eat('IDENT')  # agar
        condition = self.expression()
        then_block = self.block()

        elif_blocks = []
        else_block = None
        while self.current.kind == 'IDENT' and self.current.value == 'yahtu':
            self.eat('IDENT')
            elif_condition = self.expression()
            elif_blocks.append((elif_condition, self.block()))

        if self.current.kind == 'IDENT' and self.current.value == 'warna':
            self.eat('IDENT')
            else_block = self.block()

        return If(condition, then_block, elif_blocks, else_block)

    def while_statement(self):
        self.eat('IDENT')  # jabtak
        condition = self.expression()
        body = self.block()
        return While(condition, body)

    def for_statement(self):
        self.eat('IDENT')  # chalo
        init = self.for_init()
        self.eat('SEMICOLON')
        condition = self.expression()
        self.eat('SEMICOLON')
        increment = self.for_update()
        body = self.block()
        return For(init, condition, increment, body)

    def do_while_statement(self):
        self.eat('IDENT')  # kro
        body = self.block()
        if self.current.kind != 'IDENT' or self.current.value != 'jabtak':
            raise SyntaxError(f"Expected 'jabtak' after do-while body at line {self.current.line}")
        self.eat('IDENT')  # jabtak
        condition = self.expression()
        return DoWhile(body, condition)

    def for_init(self):
        expr = self.expression()
        if self.current.kind == 'ASSIGN' and isinstance(expr, Var):
            self.eat('ASSIGN')
            value = self.expression()
            return Assign(expr.name, value)
        return ExprStmt(expr)

    def for_update(self):
        expr = self.expression()
        if self.current.kind == 'ASSIGN' and isinstance(expr, Var):
            self.eat('ASSIGN')
            value = self.expression()
            return Assign(expr.name, value)
        return ExprStmt(expr)

    def block(self):
        self.eat('LBRACE')
        statements = []
        while self.current.kind != 'RBRACE':
            if self.current.kind == 'NEWLINE':
                self.eat('NEWLINE')
                continue
            statements.append(self.statement())
        self.eat('RBRACE')
        while self.current.kind == 'NEWLINE':
            self.eat('NEWLINE')
        return Block(statements)

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while self.current.kind == 'IDENT' and self.current.value == 'ya':
            self.eat('IDENT')
            right = self.logical_and()
            node = BinOp(node, 'OR', right)
        return node

    def logical_and(self):
        node = self.logical_not()
        while self.current.kind == 'IDENT' and self.current.value == 'aur':
            self.eat('IDENT')
            right = self.logical_not()
            node = BinOp(node, 'AND', right)
        return node

    def logical_not(self):
        if self.current.kind == 'IDENT' and self.current.value == 'nahi':
            self.eat('IDENT')
            operand = self.logical_not()
            return UnaryOp('NOT', operand)
        return self.comparison()

    def comparison(self):
        node = self.arith()
        while self.current.kind in ('EQ', 'NE', 'LT', 'LE', 'GT', 'GE'):
            op = self.eat().kind
            right = self.arith()
            node = BinOp(node, op, right)
        return node

    def arith(self):
        node = self.term()
        while self.current.kind in ('PLUS', 'MINUS'):
            op = self.eat().kind
            right = self.term()
            node = BinOp(node, op, right)
        return node

    def term(self):
        node = self.factor()
        while self.current.kind in ('MUL', 'DIV'):
            op = self.eat().kind
            right = self.factor()
            node = BinOp(node, op, right)
        return node

    def factor(self):
        token = self.current
        if token.kind in ('PLUS', 'MINUS'):
            op = self.eat().kind
            node = self.factor()
            if op == 'PLUS':
                return node
            return BinOp(Number(0), 'MINUS', node)
        if token.kind == 'NUMBER':
            self.eat('NUMBER')
            return Number(float(token.value) if '.' in token.value else int(token.value))
        if token.kind == 'STRING':
            self.eat('STRING')
            return String(eval(token.value))
        if token.kind == 'IDENT':
            if self.tokens[self.pos + 1].kind == 'LPAREN':
                return self.call()
            if token.value == 'sahi':
                self.eat('IDENT')
                return Bool(True)
            if token.value == 'galat':
                self.eat('IDENT')
                return Bool(False)
            self.eat('IDENT')
            return Var(token.value)
        if token.kind == 'LPAREN':
            self.eat('LPAREN')
            node = self.expression()
            self.eat('RPAREN')
            return node
        raise SyntaxError(f'Unexpected factor at line {token.line}: {token.kind}')

    def call(self):
        name = self.eat('IDENT').value
        self.eat('LPAREN')
        args = []
        if self.current.kind != 'RPAREN':
            args.append(self.expression())
            while self.current.kind == 'COMMA':
                self.eat('COMMA')
                args.append(self.expression())
        self.eat('RPAREN')
        return Call(name, args)

class Node: pass
class Number(Node):
    def __init__(self, value): self.value = value
class String(Node):
    def __init__(self, value): self.value = value
class Var(Node):
    def __init__(self, name): self.name = name
class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
class Call(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args
class Bool(Node):
    def __init__(self, value): self.value = value
class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
class Assign(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value
class ExprStmt(Node):
    def __init__(self, expr): self.expr = expr
class Block(Node):
    def __init__(self, statements):
        self.statements = statements
class If(Node):
    def __init__(self, condition, then_block, elif_blocks, else_block):
        self.condition = condition
        self.then_block = then_block
        self.elif_blocks = elif_blocks
        self.else_block = else_block
class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
class For(Node):
    def __init__(self, init, condition, increment, body):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body
class DoWhile(Node):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition

class Interpreter:
    def __init__(self):
        self.vars = {}

    def is_truthy(self, value):
        return bool(value)

    def eval(self, node):
        if isinstance(node, Number):
            return node.value
        if isinstance(node, String):
            return node.value
        if isinstance(node, Var):
            if node.name in self.vars:
                return self.vars[node.name]
            raise NameError(f"Undefined variable '{node.name}'")
        if isinstance(node, Bool):
            return node.value
        if isinstance(node, UnaryOp):
            value = self.eval(node.operand)
            if node.op == 'NOT':
                return not self.is_truthy(value)
            raise NameError(f"Unknown unary operator '{node.op}'")
        if isinstance(node, BinOp):
            left = self.eval(node.left)
            if node.op == 'AND':
                if not self.is_truthy(left):
                    return False
                right = self.eval(node.right)
                return self.is_truthy(right)
            if node.op == 'OR':
                if self.is_truthy(left):
                    return True
                right = self.eval(node.right)
                return self.is_truthy(right)
            right = self.eval(node.right)
            if node.op == 'PLUS':
                return left + right
            if node.op == 'MINUS':
                return left - right
            if node.op == 'MUL':
                return left * right
            if node.op == 'DIV':
                return left / right
            if node.op == 'EQ':
                return left == right
            if node.op == 'NE':
                return left != right
            if node.op == 'LT':
                return left < right
            if node.op == 'LE':
                return left <= right
            if node.op == 'GT':
                return left > right
            if node.op == 'GE':
                return left >= right
        if isinstance(node, Call):
            args = [self.eval(arg) for arg in node.args]
            if node.name == 'dikhao':
                print(*args)
                return None
            if node.name == 'btao':
                prompt = ''.join(str(arg) for arg in args)
                return input(prompt)
            raise NameError(f"Unknown function '{node.name}'")
        if isinstance(node, Assign):
            value = self.eval(node.value)
            self.vars[node.name] = value
            return value
        if isinstance(node, ExprStmt):
            return self.eval(node.expr)
        if isinstance(node, Block):
            self.execute(node.statements)
            return None
        if isinstance(node, If):
            if self.is_truthy(self.eval(node.condition)):
                self.execute(node.then_block.statements)
                return None
            for cond, block in node.elif_blocks:
                if self.is_truthy(self.eval(cond)):
                    self.execute(block.statements)
                    return None
            if node.else_block:
                self.execute(node.else_block.statements)
            return None
        if isinstance(node, While):
            while self.is_truthy(self.eval(node.condition)):
                self.execute(node.body.statements)
            return None
        if isinstance(node, For):
            self.eval(node.init)
            while self.is_truthy(self.eval(node.condition)):
                self.execute(node.body.statements)
                self.eval(node.increment)
            return None
        if isinstance(node, DoWhile):
            self.execute(node.body.statements)
            while self.is_truthy(self.eval(node.condition)):
                self.execute(node.body.statements)
            return None
        raise TypeError(f'Invalid AST node: {node}')

    def execute(self, statements):
        for stmt in statements:
            self.eval(stmt)


def run_source(source):
    tokens = tokenize(source)
    parser = Parser(tokens)
    program = parser.parse()
    interpreter = Interpreter()
    interpreter.execute(program)


def main(path):
    with open(path, 'r', encoding='utf-8') as file:
        source = file.read()
    run_source(source)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python3 toy_language.py <script.toy>')
        sys.exit(1)
    main(sys.argv[1])
