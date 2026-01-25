"""Puzzle solver and uniqueness checker."""

from puzzle import Puzzle, ALL_CHARS, build_cell_to_runs_map
from generator import could_be_valid_equation
from equation import is_valid_equation


def count_solutions(puzzle: Puzzle, max_count: int = 2) -> int:
    """Count the number of solutions to a puzzle.

    Stops counting once max_count is reached (for efficiency).
    Returns 0, 1, or max_count (meaning "at least max_count").
    """
    # Find empty cells that need to be filled
    empty_cells = [
        (r, c) for r, c in puzzle.get_active_cells()
        if puzzle.get_cell(r, c) is None
    ]

    if not empty_cells:
        # All filled - check if valid
        return 1 if puzzle.is_solved() else 0

    cell_to_runs = build_cell_to_runs_map(puzzle.shape)
    solutions = [0]  # Use list to allow modification in nested function

    def get_run_chars(run: list[tuple[int, int]]) -> list[str | None]:
        return [puzzle.get_cell(r, c) for r, c in run]

    def solve(cell_idx: int) -> bool:
        """Returns True if we should stop searching."""
        if solutions[0] >= max_count:
            return True

        if cell_idx >= len(empty_cells):
            # Check if all runs are valid
            if puzzle.is_valid():
                solutions[0] += 1
            return solutions[0] >= max_count

        row, col = empty_cells[cell_idx]
        runs = cell_to_runs[(row, col)]

        for char in ALL_CHARS:
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
                    if not is_valid_equation(run_chars):
                        valid = False
                        break

            if valid:
                if solve(cell_idx + 1):
                    puzzle.set_cell(row, col, None)
                    return True

            puzzle.set_cell(row, col, None)

        return False

    solve(0)
    return solutions[0]


def has_unique_solution(puzzle: Puzzle) -> bool:
    """Check if puzzle has exactly one solution."""
    return count_solutions(puzzle, max_count=2) == 1


def find_all_solutions(puzzle: Puzzle, max_solutions: int = 100) -> list[Puzzle]:
    """Find all solutions to a puzzle (up to max_solutions)."""
    empty_cells = [
        (r, c) for r, c in puzzle.get_active_cells()
        if puzzle.get_cell(r, c) is None
    ]

    if not empty_cells:
        return [puzzle.copy()] if puzzle.is_solved() else []

    cell_to_runs = build_cell_to_runs_map(puzzle.shape)
    solutions = []

    def get_run_chars(run: list[tuple[int, int]]) -> list[str | None]:
        return [puzzle.get_cell(r, c) for r, c in run]

    def solve(cell_idx: int):
        if len(solutions) >= max_solutions:
            return

        if cell_idx >= len(empty_cells):
            if puzzle.is_valid():
                solutions.append(puzzle.copy())
            return

        row, col = empty_cells[cell_idx]
        runs = cell_to_runs[(row, col)]

        for char in ALL_CHARS:
            puzzle.set_cell(row, col, char)

            valid = True
            for run in runs:
                run_chars = get_run_chars(run)
                if not could_be_valid_equation(run_chars):
                    valid = False
                    break
                if None not in run_chars:
                    if not is_valid_equation(run_chars):
                        valid = False
                        break

            if valid:
                solve(cell_idx + 1)

            puzzle.set_cell(row, col, None)

    solve(0)
    return solutions
