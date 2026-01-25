"""Growth-based puzzle generator.

Instead of filling a predefined shape, this grows puzzles by:
1. Generating random interesting equations
2. Placing them and finding valid intersections
3. Growing the puzzle until desired complexity
"""

import random
from dataclasses import dataclass, field

from equation import (
    DIGIT_CHARS,
    OPERATOR_CHARS,
    Operator,
    is_interesting_equation,
    is_valid_equation,
)


@dataclass
class GrowingPuzzle:
    """A puzzle that grows by adding equations."""

    cells: dict[tuple[int, int], str] = field(default_factory=dict)
    equations: list[tuple[str, list[tuple[int, int]]]] = field(default_factory=list)
    # direction, list of (row, col) positions
    cell_directions: dict[tuple[int, int], set[str]] = field(default_factory=dict)
    # Track which directions each cell is part of

    def get_cell(self, row: int, col: int) -> str | None:
        return self.cells.get((row, col))

    def set_cell(self, row: int, col: int, value: str) -> None:
        self.cells[(row, col)] = value

    def get_bounds(self) -> tuple[int, int, int, int]:
        """Get (min_row, min_col, max_row, max_col)."""
        if not self.cells:
            return (0, 0, 0, 0)
        rows = [r for r, c in self.cells]
        cols = [c for r, c in self.cells]
        return (min(rows), min(cols), max(rows), max(cols))

    def normalize(self) -> "GrowingPuzzle":
        """Shift all coordinates so min is (0, 0)."""
        if not self.cells:
            return self
        min_row, min_col, _, _ = self.get_bounds()
        new_cells = {
            (r - min_row, c - min_col): v for (r, c), v in self.cells.items()
        }
        new_equations = [
            (direction, [(r - min_row, c - min_col) for r, c in positions])
            for direction, positions in self.equations
        ]
        new_cell_directions = {
            (r - min_row, c - min_col): dirs
            for (r, c), dirs in self.cell_directions.items()
        }
        return GrowingPuzzle(
            cells=new_cells,
            equations=new_equations,
            cell_directions=new_cell_directions,
        )

    def __str__(self) -> str:
        if not self.cells:
            return "(empty)"
        p = self.normalize()
        min_row, min_col, max_row, max_col = p.get_bounds()
        lines = []
        for row in range(min_row, max_row + 1):
            line = ""
            for col in range(min_col, max_col + 1):
                cell = p.get_cell(row, col)
                line += cell if cell else " "
            lines.append(line)
        return "\n".join(lines)


def generate_interesting_equation(length: int, max_attempts: int = 1000) -> list[str] | None:
    """Generate a random interesting equation of given length.

    Returns a list of characters, or None if failed.
    """
    # For short equations (length 5), we can enumerate patterns
    # Pattern: NUM OP NUM = NUM (5 chars minimum: a+b=c)

    for _ in range(max_attempts):
        chars = _generate_random_equation(length)
        if chars and is_interesting_equation(chars):
            return chars
    return None


def _generate_random_equation(length: int) -> list[str] | None:
    """Generate a random valid equation of given length."""
    if length < 5:
        return None  # Minimum: a+b=c

    # Strategy: pick random numbers and operators, then compute result
    # For length 5: N op N = N (single digits)
    # For length 7: NN op N = NN or N op NN = NN, etc.

    ops = ["+", "-", "×", "÷"]

    for _ in range(100):  # Inner attempts
        # Decide structure based on length
        if length == 5:
            # a op b = c
            a = random.randint(1, 9)
            b = random.randint(2, 9)  # Avoid 0, 1 for more interesting math
            op = random.choice(ops)
            result = _apply_op(a, op, b)
            if result is not None and 0 <= result <= 9:
                eq = f"{a}{op}{b}={result}"
                if len(eq) == length:
                    return list(eq)

        elif length == 7:
            # Options: ab op c = de, a op bc = de, a op b = cd (if result is 2-digit)
            structures = [
                lambda: _try_structure_7_v1(),  # ab op c = de
                lambda: _try_structure_7_v2(),  # a op bc = de
                lambda: _try_structure_7_v3(),  # a op b op c = d
            ]
            random.shuffle(structures)
            for struct in structures:
                eq = struct()
                if eq and len(eq) == length:
                    return list(eq)

        elif length == 9:
            # More complex: ab op cd = ef, abc op d = efg, etc.
            eq = _try_structure_9()
            if eq and len(eq) == length:
                return list(eq)

        else:
            # For other lengths, try variations
            eq = _try_generic_structure(length)
            if eq and len(eq) == length:
                return list(eq)

    return None


def _apply_op(a: int, op: str, b: int) -> int | None:
    """Apply operator, return None if invalid."""
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "×" or op == "*":
        return a * b
    elif op == "÷" or op == "/":
        if b == 0 or a % b != 0:
            return None
        return a // b
    return None


def _try_structure_7_v1() -> str | None:
    """ab op c = de"""
    ab = random.randint(10, 99)
    c = random.randint(2, 9)
    op = random.choice(["+", "-", "×", "÷"])
    result = _apply_op(ab, op, c)
    if result is not None and 10 <= result <= 99:
        return f"{ab}{op}{c}={result}"
    return None


def _try_structure_7_v2() -> str | None:
    """a op bc = de"""
    a = random.randint(2, 9)
    bc = random.randint(10, 99)
    op = random.choice(["+", "-", "×", "÷"])
    result = _apply_op(a, op, bc)
    if result is not None and 10 <= result <= 99:
        return f"{a}{op}{bc}={result}"
    return None


def _try_structure_7_v3() -> str | None:
    """a op b op c = d (two operations)"""
    a = random.randint(1, 9)
    b = random.randint(2, 9)
    c = random.randint(2, 9)
    op1 = random.choice(["+", "-", "×"])
    op2 = random.choice(["+", "-"])

    # Evaluate left to right
    temp = _apply_op(a, op1, b)
    if temp is None:
        return None
    result = _apply_op(temp, op2, c)
    if result is not None and 0 <= result <= 9:
        return f"{a}{op1}{b}{op2}{c}={result}"
    return None


def _try_structure_9() -> str | None:
    """Various 9-char structures."""
    structures = [
        _try_9_abc_op_d_efgh,  # abc op d = efgh (unlikely)
        _try_9_ab_op_cd_efg,   # ab op cd = efg
        _try_9_a_op_b_op_c_de, # a op b op c = de
    ]
    random.shuffle(structures)
    for s in structures:
        eq = s()
        if eq:
            return eq
    return None


def _try_9_ab_op_cd_efg() -> str | None:
    """ab op cd = efg"""
    ab = random.randint(10, 99)
    cd = random.randint(10, 99)
    op = random.choice(["+", "-", "×"])
    result = _apply_op(ab, op, cd)
    if result is not None and 100 <= result <= 999:
        return f"{ab}{op}{cd}={result}"
    return None


def _try_9_abc_op_d_efgh() -> str | None:
    """abc op d = efgh (needs multiplication)"""
    abc = random.randint(100, 999)
    d = random.randint(2, 9)
    result = abc * d
    if 1000 <= result <= 9999:
        return f"{abc}×{d}={result}"
    return None


def _try_9_a_op_b_op_c_de() -> str | None:
    """a op b op c = de"""
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    c = random.randint(2, 9)
    op1 = random.choice(["+", "-", "×"])
    op2 = random.choice(["+", "-", "×"])

    temp = _apply_op(a, op1, b)
    if temp is None:
        return None
    result = _apply_op(temp, op2, c)
    if result is not None and 10 <= result <= 99:
        return f"{a}{op1}{b}{op2}{c}={result}"
    return None


def _try_generic_structure(length: int) -> str | None:
    """Try to generate equation of arbitrary length."""
    # Simple approach: num op num = num, adjust digit counts
    # length = len(a) + 1 + len(b) + 1 + len(result)

    for _ in range(50):
        # Random split of digits
        total_digits = length - 2  # minus op and =

        if total_digits < 3:
            return None

        # Try different splits
        for a_len in range(1, total_digits - 1):
            for b_len in range(1, total_digits - a_len):
                r_len = total_digits - a_len - b_len
                if r_len < 1:
                    continue

                a_min = 10 ** (a_len - 1) if a_len > 1 else 1
                a_max = 10 ** a_len - 1
                b_min = 10 ** (b_len - 1) if b_len > 1 else 2
                b_max = 10 ** b_len - 1
                r_min = 10 ** (r_len - 1) if r_len > 1 else 0
                r_max = 10 ** r_len - 1

                a = random.randint(a_min, a_max)
                b = random.randint(b_min, b_max)
                op = random.choice(["+", "-", "×"])

                result = _apply_op(a, op, b)
                if result is not None and r_min <= result <= r_max:
                    eq = f"{a}{op}{b}={result}"
                    if len(eq) == length:
                        return eq

    return None


def find_crossing_equation(
    puzzle: GrowingPuzzle,
    cross_row: int,
    cross_col: int,
    direction: str,  # "vertical" or "horizontal"
    length: int,
    cross_position: int,  # Position in new equation where crossing happens
    max_attempts: int = 500,
) -> list[str] | None:
    """Find an equation that crosses at the given position.

    The crossing cell already has a value that must be preserved.
    Also ensures the equation doesn't extend existing runs (would create invalid long equations).
    """
    existing_char = puzzle.get_cell(cross_row, cross_col)
    if existing_char is None:
        return None

    # Calculate start and end positions
    if direction == "vertical":
        start_r = cross_row - cross_position
        end_r = start_r + length - 1
        # Check cells just before start and just after end
        before_cell = puzzle.get_cell(start_r - 1, cross_col)
        after_cell = puzzle.get_cell(end_r + 1, cross_col)
    else:
        start_c = cross_col - cross_position
        end_c = start_c + length - 1
        before_cell = puzzle.get_cell(cross_row, start_c - 1)
        after_cell = puzzle.get_cell(cross_row, end_c + 1)

    # If there's a cell before or after, we'd extend an existing run - skip
    if before_cell is not None or after_cell is not None:
        return None

    for _ in range(max_attempts):
        eq = generate_interesting_equation(length)
        if eq is None:
            continue

        # Check if the character at cross_position matches
        if eq[cross_position] == existing_char:
            # Also verify no conflicts with other existing cells
            conflicts = False
            for i, char in enumerate(eq):
                if direction == "vertical":
                    r = cross_row - cross_position + i
                    c = cross_col
                else:
                    r = cross_row
                    c = cross_col - cross_position + i

                existing = puzzle.get_cell(r, c)
                if existing is not None and existing != char:
                    conflicts = True
                    break

            if not conflicts:
                return eq

    return None


def grow_puzzle(
    num_equations: int = 4,
    equation_length: int | tuple[int, int] = 5,
    max_attempts: int = 100,
) -> GrowingPuzzle | None:
    """Grow a puzzle with the specified number of equations.

    Args:
        num_equations: Number of equations to generate
        equation_length: Either a single length, or (min, max) for mixed lengths
        max_attempts: Maximum generation attempts

    Alternates between horizontal and vertical equations.
    """
    # Handle mixed lengths
    if isinstance(equation_length, tuple):
        min_len, max_len = equation_length
        lengths = [l for l in [5, 7, 9] if min_len <= l <= max_len]
    else:
        lengths = [equation_length]

    for _ in range(max_attempts):
        puzzle = GrowingPuzzle()

        # Start with first horizontal equation at row 0
        first_len = random.choice(lengths)
        first_eq = generate_interesting_equation(first_len)
        if first_eq is None:
            continue

        # Place it
        for col, char in enumerate(first_eq):
            puzzle.set_cell(0, col, char)
            puzzle.cell_directions.setdefault((0, col), set()).add("horizontal")
        puzzle.equations.append(("horizontal", [(0, col) for col in range(len(first_eq))]))

        # Now try to add more equations
        success = True
        for eq_num in range(1, num_equations):
            direction = "vertical" if eq_num % 2 == 1 else "horizontal"
            opposite = "horizontal" if direction == "vertical" else "vertical"

            # Find a digit cell that's on an opposite-direction equation
            # (so we can cross it without extending an existing line)
            digit_cells = [
                (r, c, v) for (r, c), v in puzzle.cells.items()
                if v in DIGIT_CHARS
                and opposite in puzzle.cell_directions.get((r, c), set())
                and direction not in puzzle.cell_directions.get((r, c), set())
            ]

            if not digit_cells:
                success = False
                break

            # Try random digit cells and lengths
            random.shuffle(digit_cells)
            placed = False

            # Try different lengths
            trial_lengths = lengths.copy()
            random.shuffle(trial_lengths)

            for eq_length in trial_lengths:
                if placed:
                    break
                for cross_row, cross_col, cross_char in digit_cells:
                    if placed:
                        break
                    # Try different crossing positions
                    for cross_pos in range(eq_length):
                        crossing_eq = find_crossing_equation(
                            puzzle, cross_row, cross_col, direction,
                            eq_length, cross_pos
                        )

                        if crossing_eq is not None:
                            # Place the equation
                            positions = []
                            for i, char in enumerate(crossing_eq):
                                if direction == "vertical":
                                    r = cross_row - cross_pos + i
                                    c = cross_col
                                else:
                                    r = cross_row
                                    c = cross_col - cross_pos + i
                                puzzle.set_cell(r, c, char)
                                puzzle.cell_directions.setdefault((r, c), set()).add(direction)
                                positions.append((r, c))

                            puzzle.equations.append((direction, positions))
                            placed = True
                            break

            if not placed:
                success = False
                break

        if success and len(puzzle.equations) == num_equations:
            return puzzle.normalize()

    return None


def grown_puzzle_to_shape_and_solution(puzzle: GrowingPuzzle):
    """Convert a grown puzzle to a Shape and solved Puzzle."""
    from shape import Shape
    from puzzle import Puzzle as PuzzleClass

    # Get bounds
    p = puzzle.normalize()
    _, _, max_row, max_col = p.get_bounds()

    # Build grid
    grid = []
    for row in range(max_row + 1):
        grid_row = []
        for col in range(max_col + 1):
            grid_row.append(p.get_cell(row, col) is not None)
        grid.append(grid_row)

    shape = Shape(grid=grid)
    solved = PuzzleClass(shape=shape, cells=dict(p.cells))

    return shape, solved


def generate_figure_eight(max_attempts: int = 1000) -> GrowingPuzzle | None:
    """Generate a figure-8 shaped puzzle (two stacked boxes sharing middle row).

    The figure-8 has:
    - 3 horizontal 5-cell equations (top, middle, bottom)
    - 2 vertical 9-cell equations (left, right sides)

    Returns a GrowingPuzzle with the figure-8 filled in, or None if failed.
    """
    from collections import defaultdict

    # Pre-generate equation pools (use fixed seeds for reproducibility, shuffle later)
    nine_cells = []
    five_cells = []

    # Generate 9-cell equations
    for i in range(500):
        eq9 = generate_interesting_equation(9)
        if eq9:
            nine_cells.append((eq9, eq9[0], eq9[4], eq9[8]))
        if len(nine_cells) >= 200:
            break

    # Generate 5-cell equations
    for i in range(500):
        eq5 = generate_interesting_equation(5)
        if eq5:
            five_cells.append((eq5, eq5[0], eq5[4]))
        if len(five_cells) >= 200:
            break

    if len(nine_cells) < 10 or len(five_cells) < 10:
        return None

    # Build lookup for 5-cell by (start, end)
    five_by_pair = defaultdict(list)
    for eq, start, end in five_cells:
        five_by_pair[(start, end)].append(eq)

    # Shuffle for randomness
    random.shuffle(nine_cells)

    # Search for valid combinations
    for left_eq, A, C, E in nine_cells:
        for right_eq, B, D, F in nine_cells:
            if left_eq == right_eq:
                continue

            top_options = five_by_pair.get((A, B), [])
            mid_options = five_by_pair.get((C, D), [])
            bot_options = five_by_pair.get((E, F), [])

            if top_options and mid_options and bot_options:
                # Pick random equations from options
                top = random.choice(top_options)
                mid = random.choice(mid_options)
                bot = random.choice(bot_options)

                # Build the puzzle
                puzzle = GrowingPuzzle()

                # Place cells - figure-8 is 5 wide, 9 tall
                # Top horizontal (row 0)
                for col, char in enumerate(top):
                    puzzle.set_cell(0, col, char)

                # Middle horizontal (row 4)
                for col, char in enumerate(mid):
                    puzzle.set_cell(4, col, char)

                # Bottom horizontal (row 8)
                for col, char in enumerate(bot):
                    puzzle.set_cell(8, col, char)

                # Left vertical (col 0, rows 0-8)
                for row, char in enumerate(left_eq):
                    puzzle.set_cell(row, 0, char)

                # Right vertical (col 4, rows 0-8)
                for row, char in enumerate(right_eq):
                    puzzle.set_cell(row, 4, char)

                return puzzle.normalize()

    return None


def generate_figure_four(max_attempts: int = 1000) -> GrowingPuzzle | None:
    """Generate a figure-4 shaped puzzle.

    Shape:
        X   X
        X   X
        X   X
        X   X
        XXXXX
            X
            X
            X
            X

    The figure-4 has:
    - 1 horizontal 5-cell equation (the crossbar)
    - 1 vertical 5-cell equation (left side, rows 0-4)
    - 1 vertical 9-cell equation (right side, rows 0-8)

    Returns a GrowingPuzzle with the figure-4 filled in, or None if failed.
    """
    from collections import defaultdict

    # Pre-generate equation pools
    nine_cells = []  # For right vertical
    five_cells = []  # For left vertical and horizontal

    for i in range(500):
        eq9 = generate_interesting_equation(9)
        if eq9:
            # Store (equation, position 4 digit) - where horizontal crosses
            nine_cells.append((eq9, eq9[4]))
        if len(nine_cells) >= 200:
            break

    for i in range(500):
        eq5 = generate_interesting_equation(5)
        if eq5:
            # Store (equation, start, end)
            five_cells.append((eq5, eq5[0], eq5[4]))
        if len(five_cells) >= 200:
            break

    if len(nine_cells) < 10 or len(five_cells) < 10:
        return None

    # Build lookups
    # Left vertical: need equations where position 4 (bottom) = some digit A
    # Horizontal: need equations where position 0 = A, position 4 = B
    # Right vertical: need equations where position 4 = B

    five_by_end = defaultdict(list)  # For left vertical (keyed by last digit)
    five_by_start_end = defaultdict(list)  # For horizontal
    nine_by_pos4 = defaultdict(list)  # For right vertical

    for eq, start, end in five_cells:
        five_by_end[end].append(eq)
        five_by_start_end[(start, end)].append(eq)

    for eq, pos4 in nine_cells:
        nine_by_pos4[pos4].append(eq)

    # Shuffle for randomness
    random.shuffle(five_cells)

    # Search: for each left vertical, find compatible horizontal and right vertical
    for left_eq, _, A in five_cells:  # A is the bottom of left vertical
        for horiz_eq, horiz_start, B in five_cells:
            if horiz_start != A:
                continue
            # horiz_eq starts with A, ends with B
            # Need right vertical with position 4 = B
            right_options = nine_by_pos4.get(B, [])
            if right_options:
                right_eq = random.choice(right_options)

                # Build the puzzle
                puzzle = GrowingPuzzle()

                # Left vertical (col 0, rows 0-4)
                for row, char in enumerate(left_eq):
                    puzzle.set_cell(row, 0, char)

                # Horizontal (row 4, cols 0-4)
                for col, char in enumerate(horiz_eq):
                    puzzle.set_cell(4, col, char)

                # Right vertical (col 4, rows 0-8)
                for row, char in enumerate(right_eq):
                    puzzle.set_cell(row, 4, char)

                return puzzle.normalize()

    return None
