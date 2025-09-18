"""Sudoku puzzle generator utilities."""
from __future__ import annotations

import random
from typing import Dict, List, Sequence, Tuple

from .solver import Board, count_solutions, is_valid_value

DIFFICULTY_CLUES: Dict[str, int] = {
    "Easy": 36,
    "Medium": 32,
    "Hard": 28,
}


def _empty_board() -> Board:
    return [[0 for _ in range(9)] for _ in range(9)]


def _find_empty(board: Board) -> Tuple[int, int] | None:
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col
    return None


def _solve_randomly(board: Board) -> bool:
    empty = _find_empty(board)
    if empty is None:
        return True
    row, col = empty

    numbers = list(range(1, 10))
    random.shuffle(numbers)
    for value in numbers:
        if is_valid_value(board, row, col, value):
            board[row][col] = value
            if _solve_randomly(board):
                return True
            board[row][col] = 0
    return False


def generate_full_solution() -> Board:
    board = _empty_board()
    _solve_randomly(board)
    return board


def _copy_board(board: Sequence[Sequence[int]]) -> Board:
    return [list(row) for row in board]


def generate_puzzle(difficulty: str) -> Tuple[Board, Board]:
    """Generate a Sudoku puzzle and its corresponding solution.

    Parameters
    ----------
    difficulty:
        One of ``"Easy"``, ``"Medium"`` or ``"Hard"``. The value controls the
        approximate number of clues that will remain in the puzzle.
    """

    difficulty_key = difficulty.capitalize()
    if difficulty_key not in DIFFICULTY_CLUES:
        raise ValueError(
            f"Unknown difficulty '{difficulty}'. "
            f"Valid options are: {', '.join(DIFFICULTY_CLUES)}"
        )

    solution = generate_full_solution()
    puzzle = _copy_board(solution)

    target_clues = DIFFICULTY_CLUES[difficulty_key]
    positions: List[Tuple[int, int]] = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    remaining_clues = 81

    for row, col in positions:
        if remaining_clues <= target_clues:
            break

        backup = puzzle[row][col]
        puzzle[row][col] = 0
        puzzle_copy = _copy_board(puzzle)
        if count_solutions(puzzle_copy, limit=2) == 1:
            remaining_clues -= 1
        else:
            puzzle[row][col] = backup

    return puzzle, solution
