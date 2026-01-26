#!/usr/bin/env python3
"""Generate the canonical puzzle book."""

import subprocess
import sys

# Book configuration: (level, shape_args, seed)
LEVELS = [
    (1, ["--large-digit", "1"], 5001),
    (2, ["--large-digit", "7"], 2003),
    (3, ["--figure-four"], 1003),
    (4, ["--figure-three"], 4004),
    (5, ["--figure-zero"], 1005),
    (6, ["--figure-eight"], 42),
    (7, ["--figure-two"], 2222),
    (8, ["--grow", "6"], 8008),
    (9, ["--grow", "7"], 9009),
    (10, ["--grow", "7"], 1010),
    # (11, ["--grow", "6", "--length", "7-9"], 1111),
    # (12, ["--grow", "7", "--length", "7-9"], 1212),
]


def main():
    for i, (level, shape_args, seed) in enumerate(LEVELS):
        # Determine prev/next links
        if level == 1:
            prev_link = "index.html"
        else:
            prev_link = f"level{level - 1}.html"

        if level == len(LEVELS):
            next_link = "coming-soon.html"
        else:
            next_link = f"level{level + 1}.html"

        output_file = f"output/book/level{level}.html"

        cmd = [
            "uv", "run", "python", "main.py",
            *shape_args,
            "-o", output_file,
            "--title", "Number Crosswords",
            "--subtitle", f"Level {level}",
            "--seed", str(seed),
            "--prev-link", prev_link,
            "--next-link", next_link,
        ]

        print(f"Generating Level {level}...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  ERROR: {result.stderr}")
            sys.exit(1)
        else:
            print(f"  Saved to {output_file}")

    print("\nDone! All levels generated.")


if __name__ == "__main__":
    main()
