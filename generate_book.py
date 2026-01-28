#!/usr/bin/env python3
"""Generate the canonical puzzle book."""

import random
import subprocess
import sys

# Book configuration: (level, puzzle_type, args, seed, options)
# puzzle_type: "standard" uses main.py, "ten-columns" uses ten_columns.py
# options is an optional dict with extra settings
LEVELS = [
    (1, "standard", ["--large-digit", "1"], 5001, {}),
    (2, "standard", ["--large-digit", "7"], 2003, {}),
    (3, "standard", ["--figure-four"], 1003, {}),
    (4, "standard", ["--figure-three"], 4004, {}),
    (5, "standard", ["--figure-zero"], 1005, {}),
    (6, "standard", ["--figure-eight"], 42, {}),
    (7, "standard", ["--figure-two"], 2850, {}),
    (8, "standard", ["--grow", "6"], 8008, {}),
    (9, "standard", ["--grow", "7"], 9009, {}),
    (10, "standard", ["--grow", "7"], 1010, {}),
    (11, "standard", ["--grow", "12", "--length", "7", "--multi-op"], 1111, {}),
    (12, "standard", ["--grow", "14", "--length", "7", "--multi-op"], 1212, {}),
    (13, "ten-columns", [], 1313, {"show_keyboard_hints": True}),
    (14, "ten-columns", [], 1414, {"show_keyboard_hints": False}),
]


def generate_ten_columns(level: int, seed: int, prev_link: str, next_link: str, options: dict) -> bool:
    """Generate a ten columns puzzle."""
    from ten_columns import find_ten_column_puzzle, generate_ten_column_grid
    from html_output import save_ten_columns_html

    random.seed(seed)
    puzzle = find_ten_column_puzzle()

    if puzzle is None:
        return False

    grid = generate_ten_column_grid(puzzle)
    save_ten_columns_html(
        grid,
        f"output/book/level{level}.html",
        title="Number Crosswords",
        subtitle=f"Level {level}",
        prev_link=prev_link,
        next_link=next_link,
        show_keyboard_hints=options.get("show_keyboard_hints", True),
    )
    return True


def main():
    total_levels = len(LEVELS)

    for level, puzzle_type, args, seed, options in LEVELS:
        # Determine prev/next links
        if level == 1:
            prev_link = "index.html"
        else:
            prev_link = f"level{level - 1}.html"

        if level == total_levels:
            next_link = "coming-soon.html"
        else:
            next_link = f"level{level + 1}.html"

        output_file = f"output/book/level{level}.html"

        print(f"Generating Level {level}...")

        if puzzle_type == "ten-columns":
            success = generate_ten_columns(level, seed, prev_link, next_link, options)
            if not success:
                print(f"  ERROR: Failed to generate ten columns puzzle")
                sys.exit(1)
            print(f"  Saved to {output_file}")

        else:  # standard
            cmd = [
                "uv", "run", "python", "main.py",
                *args,
                "-o", output_file,
                "--title", "Number Crosswords",
                "--subtitle", f"Level {level}",
                "--seed", str(seed),
                "--prev-link", prev_link,
                "--next-link", next_link,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"  ERROR: {result.stderr}")
                sys.exit(1)
            print(f"  Saved to {output_file}")

    print("\nDone! All levels generated.")


if __name__ == "__main__":
    main()
