"""HTML output generation for number crossword puzzles."""

from puzzle import Puzzle
from creator import PuzzleCreationResult


def generate_html(
    result: PuzzleCreationResult,
    title: str = "Number Crossword",
    subtitle: str = "",
    show_solution_button: bool = True,
    prev_link: str = "",
    next_link: str = "",
) -> str:
    """Generate an interactive HTML page for a puzzle."""
    puzzle = result.puzzle
    solution = result.solution
    shape = puzzle.shape

    # Build grid data
    grid_data = []
    for row in range(shape.height):
        row_data = []
        for col in range(shape.width):
            if shape.is_active(row, col):
                clue = puzzle.get_cell(row, col)
                answer = solution.get_cell(row, col)
                row_data.append({
                    "active": True,
                    "clue": clue,
                    "answer": answer,
                })
            else:
                row_data.append({"active": False})
        grid_data.append(row_data)

    # Convert to JSON for JavaScript
    import json
    grid_json = json.dumps(grid_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 5px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            font-size: 24px;
            margin-top: 0;
            margin-bottom: 20px;
        }}
        .puzzle-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }}
        .grid {{
            display: inline-block;
            background: white;
        }}
        .row {{
            display: flex;
        }}
        .cell {{
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
        }}
        .cell.inactive {{
            background: white;
        }}
        .cell.clue {{
            background: white;
            color: #333;
            border: 2px solid #333;
        }}
        .cell.input {{
            background: #d0d0d0;
            border: 2px solid #333;
        }}
        .cell.input.filled {{
            background: white;
        }}
        .cell input {{
            width: 100%;
            height: 100%;
            border: none;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            background: transparent;
            outline: none;
        }}
        .cell.correct {{
            background: #d4edda !important;
        }}
        .cell.incorrect {{
            background: #f8d7da !important;
        }}
        .buttons {{
            display: flex;
            gap: 10px;
        }}
        button {{
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border: none;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .check-btn {{
            background: #007bff;
            color: white;
        }}
        .check-btn:hover {{
            background: #0056b3;
        }}
        .clear-btn {{
            background: #6c757d;
            color: white;
        }}
        .clear-btn:hover {{
            background: #545b62;
        }}
        .solution-btn {{
            background: #28a745;
            color: white;
        }}
        .solution-btn:hover {{
            background: #1e7e34;
        }}
        .info {{
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .nav {{
            display: flex;
            justify-content: space-between;
            width: 100%;
            max-width: 300px;
            margin-top: 10px;
        }}
        .nav a {{
            padding: 10px 20px;
            background: #6c757d;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 16px;
        }}
        .nav a:hover {{
            background: #545b62;
        }}
        .nav .disabled {{
            visibility: hidden;
        }}
        .attribution {{
            margin-top: 30px;
            color: #999;
            font-size: 12px;
        }}
        .keyboard {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 5px;
            max-width: 260px;
        }}
        .key {{
            width: 48px;
            height: 48px;
            font-size: 22px;
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 4px;
            background: white;
            cursor: pointer;
        }}
        .key:hover {{
            background: #e9ecef;
        }}
        .key:active {{
            background: #dee2e6;
        }}

        /* Hide interactive elements when printing */
        @media print {{
            .keyboard, .buttons, .info, .nav, .attribution {{
                display: none !important;
            }}
            body {{
                background: white;
                margin: 0;
                padding: 0;
            }}
            .puzzle-container {{
                align-items: center;
            }}
            /* Slightly smaller cells for print to fit page */
            .cell {{
                width: 38px;
                height: 38px;
                font-size: 20px;
            }}
            .cell.input {{
                background: white;
            }}
            h1 {{
                text-align: center;
                width: 100%;
            }}
            @page {{
                margin: 0.75in;
            }}
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {f'<p class="subtitle">{subtitle}</p>' if subtitle else ''}

    <div class="puzzle-container">
        <div class="grid" id="grid"></div>

        <div class="keyboard" id="keyboard"></div>

        <div class="buttons">
            <button class="check-btn" onclick="checkSolution()">Check</button>
            <button class="clear-btn" onclick="clearInputs()">Clear</button>
            {"<button class='solution-btn' onclick='showSolution()'>Show Solution</button>" if show_solution_button else ""}
        </div>

        <div class="info">
            <p>Fill in the blanks so each row and column forms a valid equation.</p>
            <p>Equations are evaluated left-to-right (no order of operations).</p>
        </div>

        <div class="nav">
            <a href="{prev_link}" class="{'disabled' if not prev_link else ''}">Previous</a>
            <a href="index.html">Back to Puzzle Book</a>
            <a href="{next_link}" class="{'disabled' if not next_link else ''}">Next</a>
        </div>

        <div class="attribution">
            Designed by Jes and Isaac Dolan-Wolfe
        </div>
    </div>

    <script>
        const gridData = {grid_json};
        const validChars = ['0','1','2','3','4','5','6','7','8','9'];  // Only digits (operators always visible)
        let focusedInput = null;

        function buildGrid() {{
            const grid = document.getElementById('grid');
            grid.innerHTML = '';

            gridData.forEach((row, rowIdx) => {{
                const rowDiv = document.createElement('div');
                rowDiv.className = 'row';

                row.forEach((cell, colIdx) => {{
                    const cellDiv = document.createElement('div');
                    cellDiv.className = 'cell';

                    if (!cell.active) {{
                        cellDiv.className += ' inactive';
                    }} else if (cell.clue) {{
                        cellDiv.className += ' clue';
                        cellDiv.textContent = cell.clue;
                    }} else {{
                        cellDiv.className += ' input';
                        const input = document.createElement('input');
                        input.maxLength = 1;
                        input.dataset.row = rowIdx;
                        input.dataset.col = colIdx;
                        input.addEventListener('input', handleInput);
                        input.addEventListener('keydown', handleKeydown);
                        input.addEventListener('focus', () => focusedInput = input);
                        cellDiv.appendChild(input);
                    }}

                    rowDiv.appendChild(cellDiv);
                }});

                grid.appendChild(rowDiv);
            }});
        }}

        function buildKeyboard() {{
            const keyboard = document.getElementById('keyboard');
            keyboard.innerHTML = '';

            validChars.forEach(char => {{
                const key = document.createElement('button');
                key.className = 'key';
                key.textContent = char;
                key.addEventListener('click', () => insertChar(char));
                keyboard.appendChild(key);
            }});
        }}

        function insertChar(char) {{
            if (focusedInput) {{
                focusedInput.value = char;
                focusedInput.dispatchEvent(new Event('input'));
                moveToNext(focusedInput);
            }}
        }}

        function handleInput(e) {{
            const input = e.target;
            let value = input.value;

            // Normalize operators
            value = value.replace('*', '×').replace('/', '÷');

            // Filter invalid characters
            if (value && !validChars.includes(value)) {{
                input.value = '';
                return;
            }}

            input.value = value;
            input.parentElement.classList.remove('correct', 'incorrect');

            // Toggle filled class based on whether input has value
            if (value) {{
                input.parentElement.classList.add('filled');
            }} else {{
                input.parentElement.classList.remove('filled');
            }}
        }}

        function handleKeydown(e) {{
            const input = e.target;

            if (e.key === 'ArrowRight' || e.key === 'Tab') {{
                e.preventDefault();
                moveToNext(input);
            }} else if (e.key === 'ArrowLeft') {{
                e.preventDefault();
                moveToPrev(input);
            }} else if (e.key === 'ArrowDown') {{
                e.preventDefault();
                moveVertical(input, 1);
            }} else if (e.key === 'ArrowUp') {{
                e.preventDefault();
                moveVertical(input, -1);
            }} else if (e.key === 'Backspace' && !input.value) {{
                e.preventDefault();
                moveToPrev(input);
            }}
        }}

        function getInputs() {{
            return Array.from(document.querySelectorAll('.cell.input input'));
        }}

        function moveToNext(current) {{
            const inputs = getInputs();
            const idx = inputs.indexOf(current);
            if (idx < inputs.length - 1) {{
                inputs[idx + 1].focus();
            }}
        }}

        function moveToPrev(current) {{
            const inputs = getInputs();
            const idx = inputs.indexOf(current);
            if (idx > 0) {{
                inputs[idx - 1].focus();
            }}
        }}

        function moveVertical(current, direction) {{
            const row = parseInt(current.dataset.row);
            const col = parseInt(current.dataset.col);
            const newRow = row + direction;

            const target = document.querySelector(
                `.cell.input input[data-row="${{newRow}}"][data-col="${{col}}"]`
            );
            if (target) {{
                target.focus();
            }}
        }}

        function checkSolution() {{
            const inputs = getInputs();
            let allCorrect = true;

            inputs.forEach(input => {{
                const row = parseInt(input.dataset.row);
                const col = parseInt(input.dataset.col);
                const expected = gridData[row][col].answer;
                const actual = input.value;

                const cell = input.parentElement;
                if (actual === expected) {{
                    cell.classList.add('correct');
                    cell.classList.remove('incorrect');
                }} else {{
                    cell.classList.add('incorrect');
                    cell.classList.remove('correct');
                    allCorrect = false;
                }}
            }});

            if (allCorrect && inputs.every(i => i.value)) {{
                alert('Congratulations! You solved it!');
            }}
        }}

        function clearInputs() {{
            const inputs = getInputs();
            inputs.forEach(input => {{
                input.value = '';
                input.parentElement.classList.remove('correct', 'incorrect');
            }});
            if (inputs.length > 0) {{
                inputs[0].focus();
            }}
        }}

        function showSolution() {{
            const inputs = getInputs();
            inputs.forEach(input => {{
                const row = parseInt(input.dataset.row);
                const col = parseInt(input.dataset.col);
                input.value = gridData[row][col].answer;
                input.parentElement.classList.add('correct');
                input.parentElement.classList.remove('incorrect');
            }});
        }}

        // Initialize
        buildGrid();
        buildKeyboard();

        // Focus first input
        const firstInput = document.querySelector('.cell.input input');
        if (firstInput) firstInput.focus();
    </script>
</body>
</html>"""

    return html


def save_puzzle_html(
    result: PuzzleCreationResult,
    path: str,
    title: str = "Number Crossword",
    subtitle: str = "",
    show_solution_button: bool = True,
    prev_link: str = "",
    next_link: str = "",
) -> None:
    """Save a puzzle as an HTML file."""
    html = generate_html(result, title, subtitle, show_solution_button, prev_link, next_link)
    with open(path, "w") as f:
        f.write(html)
