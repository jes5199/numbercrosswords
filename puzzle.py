"""Puzzle representation and manipulation."""

from dataclasses import dataclass, field

from shape import Shape
from equation import is_valid_equation, DIGIT_CHARS, OPERATOR_CHARS, EQUALS_CHAR


# All possible cell values
ALL_CHARS = list(DIGIT_CHARS) + ["+", "-", "×", "÷", "="]


@dataclass
class Puzzle:
    """A number crossword puzzle with a shape and cell values."""

    shape: Shape
    cells: dict[tuple[int, int], str] = field(default_factory=dict)

    def get_cell(self, row: int, col: int) -> str | None:
        """Get the value of a cell, or None if empty/inactive."""
        if not self.shape.is_active(row, col):
            return None
        return self.cells.get((row, col))

    def set_cell(self, row: int, col: int, value: str | None) -> None:
        """Set the value of a cell."""
        if value is None:
            self.cells.pop((row, col), None)
        else:
            self.cells[(row, col)] = value

    def get_run_values(self, run: list[tuple[int, int]]) -> list[str | None]:
        """Get the values for all cells in a run."""
        return [self.get_cell(r, c) for r, c in run]

    def is_run_complete(self, run: list[tuple[int, int]]) -> bool:
        """Check if all cells in a run have values."""
        return all(self.get_cell(r, c) is not None for r, c in run)

    def is_run_valid(self, run: list[tuple[int, int]]) -> bool:
        """Check if a complete run forms a valid equation."""
        values = self.get_run_values(run)
        if any(v is None for v in values):
            return False
        return is_valid_equation(values)

    def get_active_cells(self) -> list[tuple[int, int]]:
        """Get all active cells in reading order (top-left to bottom-right)."""
        cells = []
        for row in range(self.shape.height):
            for col in range(self.shape.width):
                if self.shape.is_active(row, col):
                    cells.append((row, col))
        return cells

    def is_complete(self) -> bool:
        """Check if all active cells have values."""
        return all(
            self.get_cell(r, c) is not None
            for r, c in self.get_active_cells()
        )

    def is_valid(self) -> bool:
        """Check if all complete runs form valid equations."""
        for run in self.shape.get_all_runs():
            if self.is_run_complete(run) and not self.is_run_valid(run):
                return False
        return True

    def is_solved(self) -> bool:
        """Check if puzzle is complete and all equations are valid."""
        return self.is_complete() and self.is_valid()

    def copy(self) -> "Puzzle":
        """Create a copy of this puzzle."""
        return Puzzle(shape=self.shape, cells=dict(self.cells))

    def __str__(self) -> str:
        """Render the puzzle as text."""
        lines = []
        for row in range(self.shape.height):
            line = ""
            for col in range(self.shape.width):
                if self.shape.is_active(row, col):
                    val = self.get_cell(row, col)
                    line += val if val else "."
                else:
                    line += " "
            lines.append(line)
        return "\n".join(lines)


def get_runs_for_cell(
    shape: Shape, row: int, col: int
) -> list[list[tuple[int, int]]]:
    """Get all runs that contain a specific cell."""
    runs = []
    for run in shape.get_all_runs():
        if (row, col) in run:
            runs.append(run)
    return runs


def build_cell_to_runs_map(
    shape: Shape,
) -> dict[tuple[int, int], list[list[tuple[int, int]]]]:
    """Build a mapping from each cell to the runs it belongs to."""
    cell_to_runs = {}
    all_runs = shape.get_all_runs()
    for row in range(shape.height):
        for col in range(shape.width):
            if shape.is_active(row, col):
                cell_to_runs[(row, col)] = [
                    run for run in all_runs if (row, col) in run
                ]
    return cell_to_runs
