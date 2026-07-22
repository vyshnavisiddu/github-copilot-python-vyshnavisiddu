import copy
import random
from typing import List, Optional, Tuple

SIZE = 9
EMPTY = 0
Board = List[List[int]]

DIFFICULTY_CLUES = {
    'easy': 40,
    'medium': 32,
    'hard': 24,
}


def deep_copy(board: Board) -> Board:
    """Return a deep copy of the provided Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board() -> Board:
    """Create an empty 9x9 Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def check_row(board: Board, row: int, num: int) -> bool:
    """Return True if the given number is not already in the row."""
    return num not in board[row]


def check_column(board: Board, col: int, num: int) -> bool:
    """Return True if the given number is not already in the column."""
    return all(board[row][col] != num for row in range(SIZE))


def check_3x3_box(board: Board, row: int, col: int, num: int) -> bool:
    """Return True if the given number is not already in the 3x3 box."""
    start_row = (row // 3) * 3
    start_col = (col // 3) * 3

    for box_row in range(start_row, start_row + 3):
        for box_col in range(start_col, start_col + 3):
            if board[box_row][box_col] == num:
                return False

    return True


def is_safe(board: Board, row: int, col: int, num: int) -> bool:
    """Return True if placing the number at the given position is valid."""
    return (
        check_row(board, row, num)
        and check_column(board, col, num)
        and check_3x3_box(board, row, col, num)
    )


def fill_board(board: Board) -> bool:
    """Fill the board using backtracking and return whether a solution was found."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible_values = list(range(1, SIZE + 1))
                random.shuffle(possible_values)

                for candidate in possible_values:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY

                return False

    return True


def count_solutions(board: Board) -> int:
    """Count the number of solutions for a given Sudoku board."""
    solution_count = 0

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                for candidate in range(1, SIZE + 1):
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        solution_count += count_solutions(board)
                        board[row][col] = EMPTY
                        if solution_count > 1:
                            return solution_count
                return solution_count

    return solution_count + 1


def remove_cells(board: Board, target_clues: int) -> None:
    """Remove values while preserving a single unique solution."""
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if count_filled_cells(board) <= target_clues:
            break

        if board[row][col] == EMPTY:
            continue

        original_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) != 1:
            board[row][col] = original_value


def count_filled_cells(board: Board) -> int:
    """Return the number of non-empty cells in the board."""
    return sum(cell != EMPTY for row in board for cell in row)


def resolve_difficulty(difficulty: Optional[str], clues: Optional[int]) -> int:
    """Resolve the target clue count from the provided difficulty or explicit clue count."""
    if clues is not None:
        return clues

    normalized = (difficulty or 'medium').lower()
    return DIFFICULTY_CLUES.get(normalized, DIFFICULTY_CLUES['medium'])


def generate_puzzle(clues: Optional[int] = None, difficulty: Optional[str] = 'medium') -> Tuple[Board, Board]:
    """Generate a Sudoku puzzle and its solved board for a requested difficulty."""
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)

    target_clues = resolve_difficulty(difficulty, clues)
    puzzle = deep_copy(board)
    remove_cells(puzzle, target_clues)
    return puzzle, solution
