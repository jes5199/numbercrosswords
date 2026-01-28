"""Crossword puzzle where each digit 0-9 is used exactly once as a blank."""

import random
from collections import defaultdict
from typing import Optional

from grower import grow_puzzle, grown_puzzle_to_shape_and_solution
from shape import Shape
from puzzle import Puzzle


def find_digit_blanks(
    shape: Shape,
    solved: Puzzle,
) -> Optional[list[tuple[int, int]]]:
    """
    Find 10 cells to blank such that each digit 0-9 appears exactly once.

    Returns list of (row, col) positions, or None if not possible.
    """
    # Group digit cells by their value
    by_digit: dict[str, list[tuple[int, int]]] = defaultdict(list)

    for row in range(shape.height):
        for col in range(shape.width):
            if shape.is_active(row, col):
                val = solved.get_cell(row, col)
                if val and val.isdigit():
                    by_digit[val].append((row, col))

    # Check if we have at least one of each digit
    for d in '0123456789':
        if len(by_digit[d]) == 0:
            return None

    # Select one cell for each digit (randomly for variety)
    blanks = []
    for d in '0123456789':
        cell = random.choice(by_digit[d])
        blanks.append(cell)

    return blanks


def generate_crossword_digits_puzzle(
    num_equations: int = 14,
    equation_length: int = 7,
    multi_op: bool = True,
    max_attempts: int = 100,
) -> Optional[tuple[Shape, Puzzle, list[tuple[int, int]]]]:
    """
    Generate a crossword puzzle where exactly 10 blanks use digits 0-9 once each.

    Returns (shape, solved_puzzle, blank_positions) or None if generation fails.
    """
    for _ in range(max_attempts):
        grown = grow_puzzle(
            num_equations=num_equations,
            equation_length=equation_length,
            max_attempts=10000,
            multi_op=multi_op,
        )

        if grown is None:
            continue

        shape, solved = grown_puzzle_to_shape_and_solution(grown)
        blanks = find_digit_blanks(shape, solved)

        if blanks is not None:
            return shape, solved, blanks

    return None


def create_grid_data(
    shape: Shape,
    solved: Puzzle,
    blanks: list[tuple[int, int]],
) -> list[list[dict]]:
    """Create grid data for HTML output."""
    blank_set = set(blanks)
    grid_data = []

    for row in range(shape.height):
        row_data = []
        for col in range(shape.width):
            if shape.is_active(row, col):
                val = solved.get_cell(row, col)
                if (row, col) in blank_set:
                    row_data.append({
                        "active": True,
                        "clue": None,
                        "answer": val,
                    })
                else:
                    row_data.append({
                        "active": True,
                        "clue": val,
                        "answer": val,
                    })
            else:
                row_data.append({"active": False})
        grid_data.append(row_data)

    return grid_data
