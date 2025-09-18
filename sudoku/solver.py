"""Utilities for solving Sudoku boards."""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

Board = List[List[int]]


def _create_board_copy(board: Sequence[Sequence[int]]) -> Board:
    return [list(row) for row in board]


def is_valid_value(board: Board, row: int, col: int, value: int) -> bool:
    """Return True if ``value`` can be placed at ``board[row][col]``."""
    if value == 0:
        return True

    # Check row and column.
    if any(board[row][c] == value for c in range(9) if c != col):
        return False
    if any(board[r][col] == value for r in range(9) if r != row):
        return False

    # Check 3x3 subgrid.
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if (r != row or c != col) and board[r][c] == value:
                return False
    return True


def validate_board(board: Sequence[Sequence[int]]) -> bool:
    """Return True if the initial board configuration does not contain conflicts."""
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False

    for row in range(9):
        for col in range(9):
            value = board[row][col]
            if value == 0:
                continue
            if value not in range(1, 10):
                return False
            if not is_valid_value(board, row, col, value):
                return False
    return True


def _find_empty(board: Board) -> Optional[Tuple[int, int]]:
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col
    return None


def _solve_recursive(board: Board) -> bool:
    empty = _find_empty(board)
    if empty is None:
        return True
    row, col = empty

    for value in range(1, 10):
        if is_valid_value(board, row, col, value):
            board[row][col] = value
            if _solve_recursive(board):
                return True
            board[row][col] = 0
    return False


def solve_board(board: Sequence[Sequence[int]]) -> Optional[Board]:
    """Return a solved board or ``None`` if the puzzle is unsolvable."""
    working_board = _create_board_copy(board)
    if not validate_board(working_board):
        return None
    if _solve_recursive(working_board):
        return working_board
    return None


def count_solutions(board: Sequence[Sequence[int]], limit: int = 2) -> int:
    """Return the number of valid solutions up to ``limit``.

    The solver stops searching once ``limit`` solutions are found to avoid
    unnecessary work when only uniqueness is of interest.
    """

    working_board = _create_board_copy(board)
    solution_count = 0

    def backtrack() -> None:
        nonlocal solution_count
        if solution_count >= limit:
            return

        empty = _find_empty(working_board)
        if empty is None:
            solution_count += 1
            return

        row, col = empty
        for value in range(1, 10):
            if is_valid_value(working_board, row, col, value):
                working_board[row][col] = value
                backtrack()
                working_board[row][col] = 0
                if solution_count >= limit:
                    return

    backtrack()
    return solution_count
