"""Ten Columns puzzle generator.

A puzzle with 10 separate vertical equations, each with one blank.
The 10 blanks use each digit 0-9 exactly once.
"""

import random
from typing import Optional


def generate_all_equations() -> list[tuple[int, str, int, int]]:
    """Generate all valid single-digit equations: a op b = c."""
    equations = []

    for a in range(10):
        for b in range(10):
            # Addition
            c = a + b
            if 0 <= c <= 9:
                equations.append((a, '+', b, c))

            # Subtraction
            c = a - b
            if 0 <= c <= 9:
                equations.append((a, '-', b, c))

            # Multiplication
            c = a * b
            if 0 <= c <= 9:
                equations.append((a, '×', b, c))

            # Division (must divide evenly)
            if b != 0 and a % b == 0:
                c = a // b
                if 0 <= c <= 9:
                    equations.append((a, '÷', b, c))

    return equations


def is_interesting_equation(eq: tuple[int, str, int, int], blank_pos: int | None = None) -> bool:
    """Check if an equation is interesting (not trivial).

    If blank_pos is provided, considers whether the blank position makes it interesting.
    """
    a, op, b, c = eq

    # Special case: allow "a × 0 = 0" when the blank is the 0 (position 2)
    # This is the only way to have 0 as an answer that's somewhat interesting
    # e.g., "5 × _ = 0" requires thinking "what times 5 is 0?"
    if op == '×' and b == 0 and c == 0 and blank_pos == 2:
        return True

    # Reject trivial operations
    if op == '+' and (a == 0 or b == 0):
        return False
    if op == '-' and b == 0:
        return False
    if op == '×' and (a == 1 or b == 1 or a == 0 or b == 0):
        return False
    if op == '÷' and (b == 1 or a == 0):
        return False

    # Equations with repeated operands (like 6-6=0) are only interesting
    # if the blank is one of the operands, not the result
    if a == b and blank_pos == 4:
        return False

    return True


def equation_to_cells(eq: tuple[int, str, int, int]) -> list[str]:
    """Convert equation tuple to list of cell values."""
    a, op, b, c = eq
    return [str(a), op, str(b), '=', str(c)]


def find_ten_column_puzzle(
    max_attempts: int = 10000,
    require_interesting: bool = True,
) -> Optional[list[tuple[tuple[int, str, int, int], int]]]:
    """
    Find 10 equations where blanks use digits 0-9 exactly once.

    Returns list of (equation, blank_position) tuples, or None if not found.
    blank_position is 0, 2, or 4 (positions of digits in the equation).
    """
    all_equations = generate_all_equations()

    # Build index: for each digit, which (equation, position) pairs have it?
    digit_options: dict[int, list[tuple[tuple[int, str, int, int], int]]] = {
        d: [] for d in range(10)
    }

    for eq in all_equations:
        a, op, b, c = eq
        # Check if each position is interesting
        if not require_interesting or is_interesting_equation(eq, 0):
            digit_options[a].append((eq, 0))
        if not require_interesting or is_interesting_equation(eq, 2):
            digit_options[b].append((eq, 2))
        if not require_interesting or is_interesting_equation(eq, 4):
            digit_options[c].append((eq, 4))

    # Backtracking search to find 10 equations
    for _ in range(max_attempts):
        result = []
        used_equations = set()
        remaining_digits = list(range(10))
        random.shuffle(remaining_digits)

        success = True
        for digit in remaining_digits:
            options = [
                (eq, pos) for eq, pos in digit_options[digit]
                if eq not in used_equations
            ]

            if not options:
                success = False
                break

            eq, pos = random.choice(options)
            result.append((eq, pos))
            used_equations.add(eq)

        if success:
            # Sort by the blank digit for consistent ordering
            result.sort(key=lambda x: [str(x[0][0]), x[0][1], str(x[0][2]), str(x[0][3])][0])
            return result

    return None


def generate_ten_column_grid(
    puzzle: list[tuple[tuple[int, str, int, int], int]]
) -> list[list[dict]]:
    """
    Generate grid data for HTML output.

    Returns a 5x21 grid (5 rows, 10 equations with gaps between them).
    """
    grid = []

    for row in range(5):
        row_data = []
        for col_idx, (eq, blank_pos) in enumerate(puzzle):
            # Add gap between equations (except before first)
            if col_idx > 0:
                row_data.append({"active": False})

            cells = equation_to_cells(eq)
            cell_value = cells[row]

            if row == blank_pos:
                # This is the blank
                row_data.append({
                    "active": True,
                    "clue": None,
                    "answer": cell_value,
                })
            else:
                # This is a clue
                row_data.append({
                    "active": True,
                    "clue": cell_value,
                    "answer": cell_value,
                })

        grid.append(row_data)

    return grid
