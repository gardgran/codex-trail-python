"""Entry point for the Sudoku desktop application."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Sequence

from sudoku.generator import DIFFICULTY_CLUES, generate_puzzle
from sudoku.pdf import export_puzzle_to_pdf
from sudoku.solver import solve_board

Board = List[List[int]]


class SudokuApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sudoku Toolkit")
        self.root.resizable(False, False)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._entry_validator = self.root.register(self._validate_entry)

        self._solver_entries: list[list[tk.StringVar]] = []
        self._solver_status = tk.StringVar(value="")
        self._generator_cells: list[list[tk.StringVar]] = []
        self._generator_status = tk.StringVar(value="")
        self._current_generated: tuple[Board, Board] | None = None

        self._create_solver_tab()
        self._create_generator_tab()

    # ------------------------------------------------------------------
    # UI construction helpers
    # ------------------------------------------------------------------
    def _create_solver_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Solver")

        grid_frame = ttk.Frame(frame)
        grid_frame.grid(row=0, column=0, columnspan=3)

        for row in range(9):
            row_vars: list[tk.StringVar] = []
            for col in range(9):
                var = tk.StringVar()
                entry = ttk.Entry(
                    grid_frame,
                    width=2,
                    font=("Helvetica", 18),
                    justify="center",
                    textvariable=var,
                    validate="key",
                    validatecommand=(self._entry_validator, "%P"),
                )
                padx = (2, 6) if col in (2, 5) else (2, 2)
                pady = (2, 6) if row in (2, 5) else (2, 2)
                entry.grid(row=row, column=col, padx=padx, pady=pady)
                row_vars.append(var)
            self._solver_entries.append(row_vars)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(12, 0))

        solve_button = ttk.Button(button_frame, text="Solve", command=self.solve_current_board)
        solve_button.grid(row=0, column=0, padx=5)

        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_solver_board)
        clear_button.grid(row=0, column=1, padx=5)

        status_label = ttk.Label(frame, textvariable=self._solver_status, foreground="#0a7f20")
        status_label.grid(row=2, column=0, columnspan=3, pady=(8, 0))

    def _create_generator_tab(self) -> None:
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Generator")

        options_frame = ttk.Frame(frame)
        options_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        ttk.Label(options_frame, text="Difficulty:").grid(row=0, column=0, padx=(0, 6))
        self._difficulty = tk.StringVar(value="Easy")
        difficulty_select = ttk.Combobox(
            options_frame,
            textvariable=self._difficulty,
            values=list(DIFFICULTY_CLUES.keys()),
            state="readonly",
            width=8,
        )
        difficulty_select.grid(row=0, column=1)

        grid_frame = ttk.Frame(frame)
        grid_frame.grid(row=1, column=0, columnspan=3)

        for row in range(9):
            row_vars: list[tk.StringVar] = []
            for col in range(9):
                var = tk.StringVar(value="")
                label = tk.Label(
                    grid_frame,
                    width=2,
                    height=1,
                    font=("Helvetica", 18),
                    borderwidth=1,
                    relief="solid",
                    textvariable=var,
                )
                padx = (2, 6) if col in (2, 5) else (2, 2)
                pady = (2, 6) if row in (2, 5) else (2, 2)
                label.grid(row=row, column=col, padx=padx, pady=pady)
                row_vars.append(var)
            self._generator_cells.append(row_vars)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(12, 0))

        generate_button = ttk.Button(button_frame, text="Generate", command=self.generate_new_puzzle)
        generate_button.grid(row=0, column=0, padx=5)

        export_button = ttk.Button(button_frame, text="Export to PDF", command=self.export_current_puzzle)
        export_button.grid(row=0, column=1, padx=5)

        status_label = ttk.Label(frame, textvariable=self._generator_status, foreground="#0a7f20")
        status_label.grid(row=3, column=0, columnspan=3, pady=(8, 0))

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_entry(value: str) -> bool:
        if value == "":
            return True
        return len(value) == 1 and value in "123456789"

    # ------------------------------------------------------------------
    # Solver tab callbacks
    # ------------------------------------------------------------------
    def _read_solver_board(self) -> Board:
        board: Board = []
        for row_vars in self._solver_entries:
            row: list[int] = []
            for var in row_vars:
                value = var.get().strip()
                row.append(int(value) if value else 0)
            board.append(row)
        return board

    def solve_current_board(self) -> None:
        board = self._read_solver_board()
        solution = solve_board(board)
        if solution is None:
            self._solver_status.set("The puzzle is invalid or has no solution.")
            messagebox.showerror("Sudoku Solver", "The puzzle is invalid or cannot be solved.")
            return

        for row in range(9):
            for col in range(9):
                self._solver_entries[row][col].set(str(solution[row][col]))
        self._solver_status.set("Puzzle solved!")

    def clear_solver_board(self) -> None:
        for row_vars in self._solver_entries:
            for var in row_vars:
                var.set("")
        self._solver_status.set("")

    # ------------------------------------------------------------------
    # Generator tab callbacks
    # ------------------------------------------------------------------
    def _display_generated_puzzle(self, puzzle: Sequence[Sequence[int]]) -> None:
        for row in range(9):
            for col in range(9):
                value = puzzle[row][col]
                self._generator_cells[row][col].set(str(value) if value else "")

    def generate_new_puzzle(self) -> None:
        difficulty = self._difficulty.get()
        try:
            puzzle, solution = generate_puzzle(difficulty)
        except ValueError as exc:
            messagebox.showerror("Sudoku Generator", str(exc))
            return

        self._display_generated_puzzle(puzzle)
        self._current_generated = (puzzle, solution)
        self._generator_status.set(f"Generated a {difficulty.lower()} puzzle.")

    def export_current_puzzle(self) -> None:
        if not self._current_generated:
            messagebox.showinfo("Sudoku Generator", "Generate a puzzle before exporting.")
            return

        puzzle, solution = self._current_generated
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Export Sudoku Puzzle",
        )
        if not file_path:
            return

        try:
            export_puzzle_to_pdf(file_path, puzzle, solution, self._difficulty.get())
        except OSError as exc:
            messagebox.showerror("Sudoku Generator", f"Unable to export PDF: {exc}")
            return

        self._generator_status.set("Puzzle exported to PDF.")
        messagebox.showinfo("Sudoku Generator", "Puzzle exported successfully.")


def main() -> None:
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
