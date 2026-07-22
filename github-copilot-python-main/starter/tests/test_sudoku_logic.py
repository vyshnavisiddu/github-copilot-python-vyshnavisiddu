import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sudoku_logic


def test_create_empty_board_has_expected_shape():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_detects_row_column_and_box_conflicts():
    row_conflict_board = sudoku_logic.create_empty_board()
    row_conflict_board[0][0] = 1
    assert sudoku_logic.is_safe(row_conflict_board, 0, 1, 1) is False

    column_conflict_board = sudoku_logic.create_empty_board()
    column_conflict_board[0][0] = 2
    assert sudoku_logic.is_safe(column_conflict_board, 1, 0, 2) is False

    box_conflict_board = sudoku_logic.create_empty_board()
    box_conflict_board[0][0] = 3
    box_conflict_board[1][1] = 3
    assert sudoku_logic.is_safe(box_conflict_board, 2, 2, 3) is False


def test_generate_puzzle_returns_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert puzzle != solution
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) < sum(
        cell != sudoku_logic.EMPTY for row in solution for cell in row
    )
    assert all(cell != sudoku_logic.EMPTY for row in solution for cell in row)


def test_generate_puzzle_with_difficulty_has_a_unique_solution():
    for difficulty in ('easy', 'medium', 'hard'):
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

        assert len(puzzle) == sudoku_logic.SIZE
        assert len(solution) == sudoku_logic.SIZE
        assert sudoku_logic.count_solutions(puzzle) == 1
        assert puzzle != solution
