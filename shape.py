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


# Predefined puzzle shapes
# Design principle: minimize intersections, keep equations 5-7 cells
PRESET_SHAPES = {
    "cross-small": """
  X
  X
XXXXX
  X
  X
""",
    "cross-medium": """
   X
   X
   X
XXXXXXX
   X
   X
   X
""",
    "cross-large": """
    X
    X
    X
    X
XXXXXXXXX
    X
    X
    X
    X
""",
    "stairs": """
XXXXX
    X
    XXXXX
        X
        XXXXX
""",
    "stairs-long": """
XXXXX
    X
    XXXXX
        X
        XXXXX
            X
            XXXXX
""",
    "ladder": """
  X
  X
XXXXX
  X
  X
XXXXX
  X
  X
XXXXX
  X
  X
""",
}


def get_preset_shape(name: str) -> Shape:
    """Get a preset shape by name."""
    if name not in PRESET_SHAPES:
        available = ", ".join(PRESET_SHAPES.keys())
        raise ValueError(f"Unknown preset shape '{name}'. Available: {available}")
    return Shape.from_string(PRESET_SHAPES[name])


# Large digit shapes for puzzle generation
# All runs are exactly 5 cells - no 3-cell connectors
# Equations share exactly ONE corner cell
LARGE_DIGIT_SHAPES = {
    # 0 - same structure as 8 (simple down-right stair)
    0: """
XXXXX
    X
    X
    X
    XXXXX
        X
        X
        X
        XXXXX
            X
            X
            X
            XXXXX
""",
    # 1 - vertical line (single 5-cell equation)
    1: """
X
X
X
X
X
""",
    # 2 - stairs right-down-right
    2: """
XXXXX
    X
    X
    X
    XXXXX
""",
    # 3 - double L stairs
    3: """
XXXXX
    X
    X
    X
    XXXXX
        X
        X
        X
        XXXXX
""",
    # 4 - two L shapes connected
    4: """
X
X
X
X
XXXXX
    X
    X
    X
    XXXXX
""",
    # 5 - simple 3-step stair (down-right)
    5: """
XXXXX
    X
    X
    X
    XXXXX
        X
        X
        X
        XXXXX
""",
    # 6 - like digit 3 (4-step stair)
    6: """
XXXXX
    X
    X
    X
    XXXXX
        X
        X
        X
        XXXXX
            X
            X
            X
            XXXXX
""",
    # 7 - simple angle
    7: """
XXXXX
    X
    X
    X
    X
""",
    # 8 - long stairs down
    8: """
XXXXX
    X
    X
    X
    XXXXX
        X
        X
        X
        XXXXX
            X
            X
            X
            XXXXX
""",
    # 9 - stairs with tail
    9: """
XXXXX
    X
    X
    X
    XXXXX
        X
        X
        X
        X
""",
}


def get_large_digit_shape(digit: int) -> Shape:
    """Get the large shape for a digit 0-9."""
    if digit not in LARGE_DIGIT_SHAPES:
        raise ValueError(f"No large shape defined for digit {digit}")
    return Shape.from_string(LARGE_DIGIT_SHAPES[digit])
