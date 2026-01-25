"""Create puzzles by removing cells from solved puzzles."""

import random
from dataclasses import dataclass

from puzzle import Puzzle
from solver import has_unique_solution


@dataclass
class PuzzleCreationResult:
    """Result of puzzle creation."""

    puzzle: Puzzle  # The puzzle with clues (unsolved)
    solution: Puzzle  # The full solution
    num_clues: int  # Number of revealed cells
    total_cells: int  # Total number of active cells


def create_puzzle(
    solved_puzzle: Puzzle,
    min_clues: int | None = None,
    randomize: bool = True,
) -> PuzzleCreationResult:
    """Create a puzzle by removing cells while maintaining unique solution.

    Args:
        solved_puzzle: A completely solved puzzle
        min_clues: Minimum number of clues to keep (default: 30% of cells)
        randomize: Whether to randomize removal order

    Returns:
        PuzzleCreationResult with the puzzle and solution
    """
    if not solved_puzzle.is_solved():
        raise ValueError("Input puzzle must be completely solved")

    # Copy the solved puzzle
    puzzle = solved_puzzle.copy()
    solution = solved_puzzle.copy()

    cells = puzzle.get_active_cells()
    total_cells = len(cells)

    if min_clues is None:
        min_clues = max(3, total_cells // 3)

    # Get cells in removal order
    removal_order = list(cells)
    if randomize:
        random.shuffle(removal_order)

    removed_cells = []

    for row, col in removal_order:
        if total_cells - len(removed_cells) <= min_clues:
            break  # Can't remove more

        # Try removing this cell
        value = puzzle.get_cell(row, col)
        puzzle.set_cell(row, col, None)

        # Check if still has unique solution
        if has_unique_solution(puzzle):
            removed_cells.append((row, col))
        else:
            # Restore the cell
            puzzle.set_cell(row, col, value)

    return PuzzleCreationResult(
        puzzle=puzzle,
        solution=solution,
        num_clues=total_cells - len(removed_cells),
        total_cells=total_cells,
    )


def create_puzzle_with_difficulty(
    solved_puzzle: Puzzle,
    difficulty: str = "medium",
) -> PuzzleCreationResult:
    """Create a puzzle with specified difficulty.

    Difficulty levels:
    - easy: ~50% of cells revealed
    - medium: ~35% of cells revealed
    - hard: ~25% of cells revealed (minimum viable)
    """
    total = len(solved_puzzle.get_active_cells())

    clue_percentages = {
        "easy": 0.50,
        "medium": 0.35,
        "hard": 0.25,
    }

    pct = clue_percentages.get(difficulty, 0.35)
    min_clues = max(3, int(total * pct))

    return create_puzzle(solved_puzzle, min_clues=min_clues)
