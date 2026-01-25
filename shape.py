"""Shape representation for number crossword puzzles."""

from dataclasses import dataclass


@dataclass
class Shape:
    """A 2D grid shape where cells can be active or inactive."""

    grid: list[list[bool]]  # True = active cell, False = empty

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def width(self) -> int:
        return max(len(row) for row in self.grid) if self.grid else 0

    def is_active(self, row: int, col: int) -> bool:
        """Check if a cell is active (within bounds and marked)."""
        if 0 <= row < len(self.grid) and 0 <= col < len(self.grid[row]):
            return self.grid[row][col]
        return False

    def get_horizontal_runs(self) -> list[list[tuple[int, int]]]:
        """Get all horizontal runs of consecutive active cells (length >= 3)."""
        runs = []
        for row_idx, row in enumerate(self.grid):
            run = []
            for col_idx in range(len(row) + 1):
                if col_idx < len(row) and row[col_idx]:
                    run.append((row_idx, col_idx))
                else:
                    if len(run) >= 3:  # Minimum for equation: a=b or x+y
                        runs.append(run)
                    run = []
        return runs

    def get_vertical_runs(self) -> list[list[tuple[int, int]]]:
        """Get all vertical runs of consecutive active cells (length >= 3)."""
        runs = []
        for col_idx in range(self.width):
            run = []
            for row_idx in range(self.height + 1):
                if row_idx < self.height and self.is_active(row_idx, col_idx):
                    run.append((row_idx, col_idx))
                else:
                    if len(run) >= 3:
                        runs.append(run)
                    run = []
        return runs

    def get_all_runs(self) -> list[list[tuple[int, int]]]:
        """Get all horizontal and vertical runs."""
        return self.get_horizontal_runs() + self.get_vertical_runs()

    def get_active_cells(self) -> list[tuple[int, int]]:
        """Get all active cells in reading order (top-left to bottom-right)."""
        cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.is_active(row, col):
                    cells.append((row, col))
        return cells

    @classmethod
    def from_string(cls, text: str, active_char: str = "X") -> "Shape":
        """Load a shape from a text string.

        Example:
            '''
              XXX
              X
            XXXXX
              X
              XXX
            '''
        """
        # Remove leading/trailing empty lines but preserve internal whitespace
        lines = text.split("\n")
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        if not lines:
            return cls(grid=[])

        # Normalize width so all rows have same length
        max_width = max(len(line) for line in lines)
        grid = []
        for line in lines:
            # Pad line to max width
            padded = line.ljust(max_width)
            row = [c == active_char for c in padded]
            grid.append(row)
        return cls(grid=grid)

    @classmethod
    def from_file(cls, path: str, active_char: str = "X") -> "Shape":
        """Load a shape from a text file."""
        with open(path) as f:
            return cls.from_string(f.read(), active_char)

    def __str__(self) -> str:
        """Render the shape as text."""
        result = []
        for row in self.grid:
            line = "".join("X" if cell else " " for cell in row)
            result.append(line)
        return "\n".join(result)


# Predefined digit shapes
DIGIT_SHAPES = {
    0: """
 XXX
X   X
X   X
X   X
 XXX
""",
    1: """
  X
 XX
  X
  X
 XXX
""",
    2: """
 XXX
X   X
  XX
 X
XXXXX
""",
    3: """
XXXX
   X
 XXX
   X
XXXX
""",
    4: """
X  X
X  X
XXXX
   X
   X
""",
    5: """
XXXXX
X
XXXX
    X
XXXX
""",
    6: """
 XXX
X
XXXX
X   X
 XXX
""",
    7: """
XXXXX
    X
   X
  X
  X
""",
    8: """
 XXX
X   X
 XXX
X   X
 XXX
""",
    9: """
 XXX
X   X
 XXXX
    X
 XXX
""",
}


def get_digit_shape(digit: int) -> Shape:
    """Get the shape for a digit 0-9."""
    if digit not in DIGIT_SHAPES:
        raise ValueError(f"No shape defined for digit {digit}")
    return Shape.from_string(DIGIT_SHAPES[digit])
