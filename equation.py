"""Equation parsing and evaluation for number crossword puzzles.

Equations are evaluated strictly left-to-right with no operator precedence.
Example: 2+3×4 = (2+3)×4 = 20, not 2+(3×4) = 14
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union


class Operator(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "×"
    DIV = "÷"

    def apply(self, a: int, b: int) -> int | None:
        """Apply the operator. Returns None if invalid (e.g., non-integer division)."""
        match self:
            case Operator.ADD:
                return a + b
            case Operator.SUB:
                return a - b
            case Operator.MUL:
                return a * b
            case Operator.DIV:
                if b == 0 or a % b != 0:
                    return None
                return a // b


# Characters that represent operators (support both × and *, ÷ and /)
OPERATOR_CHARS = {
    "+": Operator.ADD,
    "-": Operator.SUB,
    "×": Operator.MUL,
    "*": Operator.MUL,
    "÷": Operator.DIV,
    "/": Operator.DIV,
}

DIGIT_CHARS = set("0123456789")
EQUALS_CHAR = "="


@dataclass
class ParsedEquation:
    """A parsed equation with left side, equals, and right side."""

    left_tokens: list[Union[int, Operator]]  # Numbers and operators
    right_tokens: list[Union[int, Operator]]  # Numbers and operators

    def evaluate_side(self, tokens: list[Union[int, Operator]]) -> int | None:
        """Evaluate a sequence of tokens left-to-right."""
        if not tokens:
            return None

        result = tokens[0]
        if not isinstance(result, int):
            return None

        i = 1
        while i < len(tokens):
            if i + 1 >= len(tokens):
                return None  # Operator without operand

            op = tokens[i]
            operand = tokens[i + 1]

            if not isinstance(op, Operator) or not isinstance(operand, int):
                return None

            result = op.apply(result, operand)
            if result is None:
                return None

            i += 2

        return result

    def is_valid(self) -> bool:
        """Check if the equation is valid (both sides evaluate to same value)."""
        left_val = self.evaluate_side(self.left_tokens)
        right_val = self.evaluate_side(self.right_tokens)

        if left_val is None or right_val is None:
            return False

        return left_val == right_val


def tokenize(chars: list[str]) -> list[Union[int, Operator, str]] | None:
    """Convert a list of characters to tokens.

    Returns None if invalid characters are found.
    Returns a list of: int (numbers), Operator, or '=' (equals sign)
    """
    tokens = []
    i = 0

    while i < len(chars):
        c = chars[i]

        if c in DIGIT_CHARS:
            # Accumulate digits into a number
            num_str = c
            while i + 1 < len(chars) and chars[i + 1] in DIGIT_CHARS:
                i += 1
                num_str += chars[i]
            tokens.append(int(num_str))

        elif c in OPERATOR_CHARS:
            tokens.append(OPERATOR_CHARS[c])

        elif c == EQUALS_CHAR:
            tokens.append("=")

        else:
            return None  # Invalid character

        i += 1

    return tokens


def parse_equation(chars: list[str]) -> ParsedEquation | None:
    """Parse a list of characters into an equation.

    The equation must have exactly one '=' sign.
    Returns None if parsing fails.
    """
    tokens = tokenize(chars)
    if tokens is None:
        return None

    # Find the equals sign
    equals_indices = [i for i, t in enumerate(tokens) if t == "="]
    if len(equals_indices) != 1:
        return None

    eq_idx = equals_indices[0]
    left_tokens = tokens[:eq_idx]
    right_tokens = tokens[eq_idx + 1 :]

    if not left_tokens or not right_tokens:
        return None

    # Filter out the '=' from token lists (should already be done)
    left_tokens = [t for t in left_tokens if t != "="]
    right_tokens = [t for t in right_tokens if t != "="]

    return ParsedEquation(left_tokens=left_tokens, right_tokens=right_tokens)


def has_leading_zeros(chars: list[str]) -> bool:
    """Check if any multi-digit number has a leading zero.

    E.g., "08" is invalid, but "0" alone is fine.
    """
    i = 0
    while i < len(chars):
        if chars[i] in DIGIT_CHARS:
            # Found start of a number
            num_start = i
            while i < len(chars) and chars[i] in DIGIT_CHARS:
                i += 1
            num_len = i - num_start
            # Leading zero if number has multiple digits and starts with 0
            if num_len > 1 and chars[num_start] == "0":
                return True
        else:
            i += 1
    return False


def is_valid_equation(chars: list[str]) -> bool:
    """Check if a list of characters forms a valid equation."""
    # Check for leading zeros (e.g., "08" is invalid)
    if has_leading_zeros(chars):
        return False

    parsed = parse_equation(chars)
    if parsed is None:
        return False
    return parsed.is_valid()


def get_valid_chars() -> set[str]:
    """Get the set of all valid cell characters."""
    return DIGIT_CHARS | set(OPERATOR_CHARS.keys()) | {EQUALS_CHAR}


def is_interesting_equation(chars: list[str]) -> bool:
    """Check if an equation is 'interesting' (has real math, not trivial).

    Rejects:
    - Leading zeros (e.g., 08)
    - Equations with no operators (just X=X)
    - Divide by 1 (÷1)
    - Multiply by 1 (×1)
    - Add/subtract 0 (+0, -0)
    - Multiply by 0 (×0) - result is always 0, not interesting
    - Equations that equal 0 with only one operator (e.g., 8-8=0 is just X=X in disguise)
    """
    # Use is_valid_equation which includes leading zero check
    if not is_valid_equation(chars):
        return False

    # We know it's valid, so parse should succeed
    parsed = parse_equation(chars)

    all_tokens = parsed.left_tokens + parsed.right_tokens

    # Count operators
    operator_count = sum(1 for t in all_tokens if isinstance(t, Operator))
    if operator_count == 0:
        return False

    # Check for trivial operations
    for i, token in enumerate(all_tokens):
        if isinstance(token, Operator):
            # Get the operand that follows
            if i + 1 < len(all_tokens):
                next_token = all_tokens[i + 1]
                if isinstance(next_token, int):
                    # ÷1 or ×1 is trivial
                    if token in (Operator.DIV, Operator.MUL) and next_token == 1:
                        return False
                    # +0 or -0 is trivial
                    if token in (Operator.ADD, Operator.SUB) and next_token == 0:
                        return False
                    # ×0 makes everything 0, not interesting
                    if token == Operator.MUL and next_token == 0:
                        return False

    # =0 with only one operator is trivial (like 8-8=0, essentially X=X)
    # Multiple operators are okay (like 8-4-4=0)
    result = parsed.evaluate_side(parsed.left_tokens)
    if result == 0 and operator_count == 1:
        return False

    return True
