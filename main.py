"""Number Crossword Puzzle Generator.

Generate number crossword puzzles where each row and column forms a valid equation.
Equations are evaluated left-to-right (no order of operations).
"""

import argparse
import random
import sys
from pathlib import Path

from shape import Shape, get_digit_shape, get_large_digit_shape, get_preset_shape, DIGIT_SHAPES, PRESET_SHAPES
from generator import generate_solved_puzzle
from creator import create_puzzle, create_puzzle_with_difficulty
from html_output import save_puzzle_html
from grower import grow_puzzle, grown_puzzle_to_shape_and_solution, generate_figure_eight, generate_figure_four, generate_figure_three, generate_figure_two, generate_figure_zero


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
        help="Use a small digit shape (0-9)",
    )
    shape_group.add_argument(
        "--large-digit",
        type=int,
        choices=range(10),
        help="Use a large digit shape (0-9) for bigger puzzles",
    )
    shape_group.add_argument(
        "--cross",
        action="store_true",
        help="Use a simple cross shape",
    )
    shape_group.add_argument(
        "--preset",
        type=str,
        choices=list(PRESET_SHAPES.keys()),
        help="Use a preset shape",
    )
    shape_group.add_argument(
        "--grow",
        type=int,
        metavar="N",
        help="Grow a puzzle with N equations (guarantees interesting math)",
    )
    shape_group.add_argument(
        "--figure-eight",
        action="store_true",
        help="Generate a figure-8 shaped puzzle (two 5x5 boxes stacked)",
    )
    shape_group.add_argument(
        "--figure-four",
        action="store_true",
        help="Generate a figure-4 shaped puzzle",
    )
    shape_group.add_argument(
        "--figure-three",
        action="store_true",
        help="Generate a figure-3 shaped puzzle (like 8 but no left side)",
    )
    shape_group.add_argument(
        "--figure-zero",
        action="store_true",
        help="Generate a figure-0 shaped puzzle (rectangular outline)",
    )
    shape_group.add_argument(
        "--figure-two",
        action="store_true",
        help="Generate a figure-2 shaped puzzle",
    )

    # Equation length (for --grow)
    parser.add_argument(
        "--length",
        type=str,
        default="5-9",
        help="Equation length for --grow: single (5,7,9) or range (5-9 for mixed)",
    )
    parser.add_argument(
        "--multi-op",
        action="store_true",
        help="Prefer equations with multiple operators (for --grow)",
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
        "--subtitle",
        type=str,
        default="",
        help="Puzzle subtitle (e.g., 'Level 1')",
    )
    parser.add_argument(
        "--no-solution-button",
        action="store_true",
        help="Don't include solution button in output",
    )
    parser.add_argument(
        "--prev-link",
        type=str,
        default="",
        help="URL for previous puzzle link",
    )
    parser.add_argument(
        "--next-link",
        type=str,
        default="",
        help="URL for next puzzle link",
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

    # Load or create shape, or grow puzzle
    if args.figure_eight:
        print("Generating figure-8 puzzle...")
        grown = generate_figure_eight(max_attempts=args.max_attempts)

        if grown is None:
            print("Failed to generate figure-8 puzzle.")
            sys.exit(1)

        shape, solved = grown_puzzle_to_shape_and_solution(grown)
        print("Generated figure-8 with 5 equations!")

    elif args.figure_four:
        print("Generating figure-4 puzzle...")
        grown = generate_figure_four(max_attempts=args.max_attempts)

        if grown is None:
            print("Failed to generate figure-4 puzzle.")
            sys.exit(1)

        shape, solved = grown_puzzle_to_shape_and_solution(grown)
        print("Generated figure-4 with 3 equations!")

    elif args.figure_three:
        print("Generating figure-3 puzzle...")
        grown = generate_figure_three(max_attempts=args.max_attempts)

        if grown is None:
            print("Failed to generate figure-3 puzzle.")
            sys.exit(1)

        shape, solved = grown_puzzle_to_shape_and_solution(grown)
        print("Generated figure-3 with 4 equations!")

    elif args.figure_zero:
        print("Generating figure-0 puzzle...")
        grown = generate_figure_zero(max_attempts=args.max_attempts)

        if grown is None:
            print("Failed to generate figure-0 puzzle.")
            sys.exit(1)

        shape, solved = grown_puzzle_to_shape_and_solution(grown)
        print("Generated figure-0 with 4 equations!")

    elif args.figure_two:
        print("Generating figure-2 puzzle...")
        grown = generate_figure_two(max_attempts=args.max_attempts)

        if grown is None:
            print("Failed to generate figure-2 puzzle.")
            sys.exit(1)

        shape, solved = grown_puzzle_to_shape_and_solution(grown)
        print("Generated figure-2 with 5 equations!")

    elif args.grow:
        # Parse length argument (e.g., "5", "7", "5-9")
        if "-" in args.length:
            min_len, max_len = map(int, args.length.split("-"))
            equation_length = (min_len, max_len)
            print(f"Growing puzzle with {args.grow} equations (mixed lengths {min_len}-{max_len})...")
        else:
            equation_length = int(args.length)
            print(f"Growing puzzle with {args.grow} equations (length {equation_length})...")

        grown = grow_puzzle(num_equations=args.grow, equation_length=equation_length, max_attempts=args.max_attempts, multi_op=args.multi_op)

        if grown is None:
            print("Failed to grow puzzle. Try fewer equations or increase --max-attempts.")
            sys.exit(1)

        shape, solved = grown_puzzle_to_shape_and_solution(grown)
        print(f"Grown {args.grow} equations with real math!")

    else:
        if args.shape_file:
            print(f"Loading shape from {args.shape_file}...")
            shape = Shape.from_file(args.shape_file)
        elif args.digit is not None:
            print(f"Using digit {args.digit} shape...")
            shape = get_digit_shape(args.digit)
        elif args.large_digit is not None:
            print(f"Using large digit {args.large_digit} shape...")
            shape = get_large_digit_shape(args.large_digit)
        elif args.preset:
            print(f"Using preset shape: {args.preset}...")
            shape = get_preset_shape(args.preset)
        elif args.cross:
            print("Using cross shape...")
            shape = get_preset_shape("cross-small")
        else:
            # Default: simple cross
            print("Using default cross shape...")
            shape = get_preset_shape("cross-small")

        # Generate solved puzzle
        print("Generating solved puzzle...")
        solved = generate_solved_puzzle(shape, max_attempts=args.max_attempts, require_interesting=True)

        if solved is None:
            print("Failed to generate a solved puzzle. Try a different shape or increase --max-attempts.")
            sys.exit(1)

        print("Found solution!")

    # Show shape info
    runs = shape.get_all_runs()
    print(f"Shape: {shape.width}x{shape.height}, {len(shape.get_active_cells())} cells, {len(runs)} equations")
    print()
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
        subtitle=args.subtitle,
        show_solution_button=not args.no_solution_button,
        prev_link=args.prev_link,
        next_link=args.next_link,
    )
    print(f"Saved puzzle to {output_path}")


if __name__ == "__main__":
    main()
