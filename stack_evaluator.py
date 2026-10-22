"""
Stack-Based Expression Evaluator
Course: DCOMP320 - Data Structures and Algorithms
Assignment: Stacks Implementation
Student: David Borbor Collier (ID: 905005353, Class: DIT1201F)

Evaluates arithmetic expressions from an input file using a two-stack algorithm
(operand stack and operator stack) and writes the results to an output file.
"""

import os
import sys

OPERATORS = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2
}


class Stack:
    """A simple LIFO stack implementation backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Push an item onto the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        """Return True if the stack has no items."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items in the stack."""
        return len(self._items)

    def __len__(self):
        return len(self._items)


def tokenize(expression):
    """
    Split an expression string into numbers, operators, and parentheses.
    Handles decimals, unary minus/plus signs, and validates characters.
    """
    tokens = []
    i = 0
    n = len(expression)

    while i < n:
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        previous = tokens[-1] if tokens else None
        expects_operand = (
            previous is None
            or previous == '('
            or previous in OPERATORS
        )

        # Unary + or - attached to a number
        if ch in '+-' and expects_operand:
            start = i
            sign = ch
            i += 1

            # Skip spaces after unary sign if any
            while i < n and expression[i].isspace():
                i += 1

            if i < n and expression[i] == '(':
                # e.g., -(2 + 3) -> -1 * (2 + 3)
                tokens.append(-1.0 if sign == '-' else 1.0)
                tokens.append('*')
                continue

            if i >= n or (not expression[i].isdigit() and expression[i] != '.'):
                raise ValueError(f"Unexpected operator '{sign}'")

            dot_count = 0
            num_start = i
            while i < n and (expression[i].isdigit() or expression[i] == '.'):
                if expression[i] == '.':
                    dot_count += 1
                i += 1

            num_str = expression[num_start:i]
            if dot_count > 1 or num_str == '.':
                raise ValueError(f"Invalid number '{sign}{num_str}'")

            val = float(sign + num_str)
            tokens.append(int(val) if val.is_integer() else val)
            continue

        if ch.isdigit() or ch == '.':
            start = i
            dot_count = 0
            while i < n and (expression[i].isdigit() or expression[i] == '.'):
                if expression[i] == '.':
                    dot_count += 1
                i += 1

            num_str = expression[start:i]
            if dot_count > 1 or num_str == '.':
                raise ValueError(f"Invalid number '{num_str}'")

            val = float(num_str)
            tokens.append(int(val) if val.is_integer() else val)
            continue

        if ch in OPERATORS:
            tokens.append(ch)
            i += 1
            continue

        if ch in '()':
            tokens.append(ch)
            i += 1
            continue

        raise ValueError(f"Invalid character '{ch}'")

    return tokens


def apply_operator(op, operands):
    """
    Pop operands, apply the binary operator op, and push the result back.
    Raises ValueError for invalid operands or division by zero.
    """
    if operands.size() < 2:
        raise ValueError("Missing operand")

    right = operands.pop()
    left = operands.pop()

    if op == '+':
        res = left + right
    elif op == '-':
        res = left - right
    elif op == '*':
        res = left * right
    elif op == '/':
        if right == 0:
            raise ValueError("Division by zero")
        res = left / right
    else:
        raise ValueError(f"Unknown operator '{op}'")

    if isinstance(res, float) and res.is_integer():
        res = int(res)
    operands.push(res)


def evaluate_expression(expression):
    """
    Evaluate an arithmetic infix expression using Dijkstra's two-stack algorithm.
    Returns numeric result (int or float).
    Raises ValueError on syntax errors or invalid arithmetic (e.g. division by zero).
    """
    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("Empty expression")

    operands = Stack()
    operators = Stack()
    expects_operand = True

    for token in tokens:
        if isinstance(token, (int, float)):
            if not expects_operand:
                raise ValueError("Missing operator between operands")
            operands.push(token)
            expects_operand = False

        elif token == '(':
            if not expects_operand:
                raise ValueError("Missing operator before '('")
            operators.push(token)

        elif token == ')':
            if expects_operand:
                raise ValueError("Unbalanced parentheses")
            while not operators.is_empty() and operators.peek() != '(':
                apply_operator(operators.pop(), operands)

            if operators.is_empty():
                raise ValueError("Unbalanced parentheses")
            operators.pop()  # Discard '('

        elif token in OPERATORS:
            if expects_operand:
                raise ValueError(f"Unexpected operator '{token}'")

            while (not operators.is_empty()
                   and operators.peek() != '('
                   and OPERATORS.get(operators.peek(), 0) >= OPERATORS[token]):
                apply_operator(operators.pop(), operands)

            operators.push(token)
            expects_operand = True

    if expects_operand:
        raise ValueError("Missing operand")

    while not operators.is_empty():
        op = operators.pop()
        if op == '(':
            raise ValueError("Unbalanced parentheses")
        apply_operator(op, operands)

    if operands.size() != 1:
        raise ValueError("Malformed expression")

    res = operands.pop()
    return int(res) if isinstance(res, float) and res.is_integer() else res


def format_result(value):
    """Format the calculated result: omit trailing .0 and round decimals to 6 places."""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        rounded = round(value, 6)
        return f"{rounded:g}"
    return str(value)


def is_separator(line):
    """Check if a line is a separator (e.g., '-----')."""
    s = line.strip()
    return len(s) >= 3 and set(s) == {'-'}


def process_file(input_file="input.txt", output_file="output.txt"):
    """
    Read expressions from input_file, evaluate each, and write results to output_file
    preserving separator lines.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if is_separator(stripped):
            output_lines.append(stripped)
        else:
            try:
                result = evaluate_expression(stripped)
                output_lines.append(format_result(result))
            except Exception as err:
                output_lines.append(f"Error: {err}")

    with open(output_file, "w", encoding="utf-8") as f:
        for out in output_lines:
            f.write(out + "\n")

    return output_lines


def main():
    """Command-line entry point."""
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output.txt"

    print(f"Reading expressions from: {input_file}")
    results = process_file(input_file, output_file)
    print(f"Evaluation complete. Results written to: {output_file}")


if __name__ == "__main__":
    main()
