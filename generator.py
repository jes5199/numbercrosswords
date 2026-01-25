"""Puzzle generator using constraint satisfaction."""

import random
from typing import Iterator

from shape import Shape
from puzzle import Puzzle, ALL_CHARS, build_cell_to_runs_map
from equation import (
    DIGIT_CHARS,
    OPERATOR_CHARS,
    EQUALS_CHAR,
    parse_equation,
    tokenize,
    Operator,
)


def could_be_valid_equation(chars: list[str | None]) -> bool:
    """Check if a partial sequence could still become a valid equation.

    This is a heuristic check for pruning - returns True if the sequence
    might still become valid, False if it definitely cannot.
    """
    filled = [c for c in chars if c is not None]

    if not filled:
        return True

    # Count equals signs - must have exactly one in final equation
    equals_count = filled.count("=")
    none_count = chars.count(None)

    if equals_count > 1:
        return False  # Too many equals

    if equals_count == 0 and none_count == 0:
        return False  # No equals and no room for one

    # Check for invalid sequences
    for i in range(len(filled) - 1):
        curr, next_char = filled[i], filled[i + 1]

        # Two operators in a row (including =) is invalid
        if curr in OPERATOR_CHARS and next_char in OPERATOR_CHARS:
            return False
        if curr in OPERATOR_CHARS and next_char == "=":
            return False
        if curr == "=" and next_char in OPERATOR_CHARS:
            return False
        if curr == "=" and next_char == "=":
            return False

    # Can't start with operator or equals
    if filled[0] in OPERATOR_CHARS or filled[0] == "=":
        return False

    # Can't end with operator (if complete)
    if none_count == 0 and filled[-1] in OPERATOR_CHARS:
        return False

    return True


def get_valid_chars_for_position(
    chars: list[str | None], pos: int
) -> list[str]:
    """Get characters that could validly go at a position in a partial run."""
    valid = []

    for char in ALL_CHARS:
        test_chars = chars.copy()
        test_chars[pos] = char

        # Quick structural checks
        if not could_be_valid_equation(test_chars):
            continue

        # If the run is now complete, do full validation
        if None not in test_chars:
            from equation import is_valid_equation

            if not is_valid_equation(test_chars):
                continue

        valid.append(char)

    return valid


def generate_solved_puzzle(
    shape: Shape, max_attempts: int = 1000, randomize: bool = True
) -> Puzzle | None:
    """Generate a solved puzzle for the given shape using backtracking.

    Returns None if no solution is found within max_attempts backtracks.
    """
    puzzle = Puzzle(shape=shape)
    cells = puzzle.get_active_cells()
    cell_to_runs = build_cell_to_runs_map(shape)

    attempts = 0

    def get_run_chars(run: list[tuple[int, int]]) -> list[str | None]:
        return [puzzle.get_cell(r, c) for r, c in run]

    def solve(cell_idx: int) -> bool:
        nonlocal attempts

        if cell_idx >= len(cells):
            return True  # All cells filled

        attempts += 1
        if attempts > max_attempts:
            return False

        row, col = cells[cell_idx]
        runs = cell_to_runs[(row, col)]

        # Find valid characters for this position
        candidates = set(ALL_CHARS)

        for run in runs:
            pos_in_run = run.index((row, col))
            run_chars = get_run_chars(run)
            valid_for_run = get_valid_chars_for_position(run_chars, pos_in_run)
            candidates &= set(valid_for_run)

        candidates = list(candidates)
        if randomize:
            random.shuffle(candidates)

        for char in candidates:
            puzzle.set_cell(row, col, char)

            # Check all affected runs
            valid = True
            for run in runs:
                run_chars = get_run_chars(run)
                if not could_be_valid_equation(run_chars):
                    valid = False
                    break
                # If run is complete, check full validity
                if None not in run_chars:
                    from equation import is_valid_equation

                    if not is_valid_equation(run_chars):
                        valid = False
                        break

            if valid and solve(cell_idx + 1):
                return True

            puzzle.set_cell(row, col, None)

        return False

    if solve(0):
        return puzzle
    return None


def generate_multiple_solutions(
    shape: Shape, max_solutions: int = 10, max_attempts: int = 10000
) -> Iterator[Puzzle]:
    """Generate multiple different solved puzzles for a shape."""
    seen = set()
    attempts = 0

    while len(seen) < max_solutions and attempts < max_attempts:
        attempts += 1
        puzzle = generate_solved_puzzle(shape, max_attempts=1000)
        if puzzle:
            key = tuple(sorted(puzzle.cells.items()))
            if key not in seen:
                seen.add(key)
                yield puzzle
