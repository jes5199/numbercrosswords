#!/usr/bin/env python3
"""Generate the canonical puzzle book with caching."""

import hashlib
import json
import os
import random
import subprocess
import sys
from pathlib import Path

# Book configuration: (level, puzzle_type, args, seed, options)
# puzzle_type: "standard" uses main.py, "ten-columns" uses ten_columns.py,
#              "crossword-digits" uses crossword_digits.py
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
    (15, "crossword-digits", [], 1500, {"show_keyboard_hints": False}),
    (16, "crossword-digits", [], 1600, {"show_keyboard_hints": False}),
    (17, "crossword-digits", [], 1704, {"show_keyboard_hints": False, "num_equations": 18}),
    (18, "crossword-digits", [], 1802, {"show_keyboard_hints": True, "num_equations": 20, "blanks_per_digit": 2}),
]

# Source files that affect puzzle generation
SOURCE_FILES = {
    "standard": [
        "main.py",
        "html_output.py",
        "generator.py",
        "grower.py",
        "equation.py",
        "shape.py",
        "puzzle.py",
        "creator.py",
    ],
    "ten-columns": [
        "ten_columns.py",
        "html_output.py",
    ],
    "crossword-digits": [
        "crossword_digits.py",
        "html_output.py",
        "grower.py",
    ],
}

CACHE_FILE = Path(".book_cache.json")


def hash_file(filepath: str) -> str:
    """Get SHA256 hash of a file's contents."""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def get_source_hash(puzzle_type: str) -> str:
    """Get combined hash of all source files for a puzzle type."""
    hashes = []
    for filename in SOURCE_FILES.get(puzzle_type, []):
        if os.path.exists(filename):
            hashes.append(hash_file(filename))
    return hashlib.sha256("".join(hashes).encode()).hexdigest()[:16]


def get_level_cache_key(
    level: int,
    puzzle_type: str,
    args: list,
    seed: int,
    options: dict,
    prev_link: str,
    next_link: str,
) -> str:
    """Generate a cache key for a level configuration."""
    config = {
        "level": level,
        "puzzle_type": puzzle_type,
        "args": args,
        "seed": seed,
        "options": options,
        "prev_link": prev_link,
        "next_link": next_link,
        "source_hash": get_source_hash(puzzle_type),
    }
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.sha256(config_str.encode()).hexdigest()[:16]


def load_cache() -> dict:
    """Load the cache manifest."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    """Save the cache manifest."""
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


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


def generate_crossword_digits(level: int, seed: int, prev_link: str, next_link: str, options: dict) -> bool:
    """Generate a crossword puzzle where each digit 0-9 is used exactly once."""
    from crossword_digits import generate_crossword_digits_puzzle, create_grid_data
    from html_output import save_crossword_digits_html

    random.seed(seed)
    result = generate_crossword_digits_puzzle(
        num_equations=options.get("num_equations", 14),
        equation_length=7,
        multi_op=True,
        max_attempts=100,
        blanks_per_digit=options.get("blanks_per_digit", 1),
    )

    if result is None:
        return False

    shape, solved, blanks = result
    grid = create_grid_data(shape, solved, blanks)
    save_crossword_digits_html(
        grid,
        f"output/book/level{level}.html",
        title="Number Crosswords",
        subtitle=f"Level {level}",
        prev_link=prev_link,
        next_link=next_link,
        show_keyboard_hints=options.get("show_keyboard_hints", False),
        blanks_per_digit=options.get("blanks_per_digit", 1),
    )
    return True


def main():
    # Parse arguments
    force_rebuild = "--force" in sys.argv or "-f" in sys.argv

    total_levels = len(LEVELS)
    cache = load_cache()
    generated = 0
    skipped = 0

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
        cache_key = get_level_cache_key(level, puzzle_type, args, seed, options, prev_link, next_link)

        # Check cache
        if not force_rebuild:
            cached_key = cache.get(f"level{level}")
            if cached_key == cache_key and os.path.exists(output_file):
                print(f"Level {level}: cached (skipping)")
                skipped += 1
                continue

        print(f"Generating Level {level}...")

        if puzzle_type == "ten-columns":
            success = generate_ten_columns(level, seed, prev_link, next_link, options)
            if not success:
                print(f"  ERROR: Failed to generate ten columns puzzle")
                sys.exit(1)
            print(f"  Saved to {output_file}")

        elif puzzle_type == "crossword-digits":
            success = generate_crossword_digits(level, seed, prev_link, next_link, options)
            if not success:
                print(f"  ERROR: Failed to generate crossword-digits puzzle")
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

        # Update cache
        cache[f"level{level}"] = cache_key
        generated += 1

    save_cache(cache)
    print(f"\nDone! Generated {generated}, skipped {skipped} cached levels.")
    if not force_rebuild and skipped > 0:
        print("Use --force to regenerate all levels.")


if __name__ == "__main__":
    main()
