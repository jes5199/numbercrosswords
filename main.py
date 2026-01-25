"""Number Crossword Puzzle Generator.

Generate number crossword puzzles where each row and column forms a valid equation.
Equations are evaluated left-to-right (no order of operations).
"""

import argparse
import random
import sys
from pathlib import Path

from shape import Shape, get_digit_shape, DIGIT_SHAPES
from generator import generate_solved_puzzle
from creator import create_puzzle, create_puzzle_with_difficulty
from html_output import save_puzzle_html


def main():
    parser = argparse.ArgumentParser(
        description="Generate number crossword puzzles"
    )

    # Shape options
    shape_group = parser.add_mutually_exclusive_group()
    shape_group.add_argument(
        "--shape-file",
        type=str,
        help="Path to a shape file (X marks active cells)",
    )
    shape_group.add_argument(
        "--digit",
        type=int,
        choices=range(10),
        help="Use a digit shape (0-9)",
    )
    shape_group.add_argument(
        "--cross",
        action="store_true",
        help="Use a simple cross shape",
    )

    # Difficulty
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Puzzle difficulty (default: medium)",
    )

    # Output options
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="puzzle.html",
        help="Output HTML file path (default: puzzle.html)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Number Crossword",
        help="Puzzle title",
    )
    parser.add_argument(
        "--no-solution-button",
        action="store_true",
        help="Don't include solution button in output",
    )

    # Generation options
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible puzzles",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=100000,
        help="Maximum attempts for puzzle generation",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print puzzle to console",
    )

    args = parser.parse_args()

    # Set random seed
    if args.seed is not None:
        random.seed(args.seed)

    # Load or create shape
    if args.shape_file:
        print(f"Loading shape from {args.shape_file}...")
        shape = Shape.from_file(args.shape_file)
    elif args.digit is not None:
        print(f"Using digit {args.digit} shape...")
        shape = get_digit_shape(args.digit)
    elif args.cross:
        print("Using cross shape...")
        shape = Shape.from_string("""
    X
    X
XXXXXXX
    X
    X
""")
    else:
        # Default: simple cross
        print("Using default cross shape...")
        shape = Shape.from_string("""
    X
    X
XXXXXXX
    X
    X
""")

    # Show shape info
    runs = shape.get_all_runs()
    print(f"Shape: {shape.width}x{shape.height}, {len(shape.get_active_cells())} cells, {len(runs)} equations")
    print()

    # Generate solved puzzle
    print("Generating solved puzzle...")
    solved = generate_solved_puzzle(shape, max_attempts=args.max_attempts)

    if solved is None:
        print("Failed to generate a solved puzzle. Try a different shape or increase --max-attempts.")
        sys.exit(1)

    print("Found solution!")
    if args.print:
        print(solved)
        print()

    # Create puzzle
    print(f"Creating {args.difficulty} puzzle...")
    result = create_puzzle_with_difficulty(solved, difficulty=args.difficulty)
    print(f"Puzzle has {result.num_clues}/{result.total_cells} clues revealed")

    if args.print:
        print()
        print("Puzzle:")
        print(result.puzzle)
        print()
        print("Solution:")
        print(result.solution)
        print()

    # Save HTML
    output_path = Path(args.output)
    save_puzzle_html(
        result,
        str(output_path),
        title=args.title,
        show_solution_button=not args.no_solution_button,
    )
    print(f"Saved puzzle to {output_path}")


if __name__ == "__main__":
    main()
