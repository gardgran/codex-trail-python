# Sudoku Toolkit

A desktop application built with Tkinter for solving Sudoku puzzles and generating new ones. The app offers two primary workflows:

- **Sudoku Solver** – enter the known digits of a puzzle, click **Solve**, and the grid is completed automatically.
- **Puzzle Generator** – create new Sudoku boards at easy, medium, or hard difficulty. Generated puzzles can be exported as PDF files that include both the puzzle and its solution.

## Getting started

This project uses only the Python standard library.

1. Ensure you have Python 3.10 or newer installed.
2. From the repository root, run the application:

   ```bash
   python app.py
   ```

## Features

- Intuitive 9×9 grid for entering Sudoku puzzles with validation for digits 1–9.
- Backtracking solver that detects invalid or unsolvable inputs.
- Random puzzle generation with guaranteed unique solutions.
- Export generated puzzles to PDF (no external libraries required).

## PDF exports

When you export a puzzle, choose the destination filename (for example `my-puzzle.pdf`). The generated PDF includes:

- The selected difficulty level.
- The puzzle grid using `.` characters to represent empty cells.
- The full solution grid.

## Development notes

- Sudoku solving and generation logic lives in the `sudoku/` package.
- PDF files are produced using a small, purpose-built writer in `sudoku/pdf.py`.

Feel free to extend the interface with additional features such as loading puzzles from files or adding pencil marks.
