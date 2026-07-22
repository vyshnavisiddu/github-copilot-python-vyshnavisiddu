"""Route definitions for the Sudoku Flask application."""

from flask import Blueprint, current_app, jsonify, render_template, request

import sudoku_logic

main_bp = Blueprint('main', __name__)


def get_game_store():
    """Return the configured in-memory game store."""
    game_store = current_app.extensions.get('game_store')
    if game_store is None:
        raise RuntimeError('Game store is not configured')
    return game_store


@main_bp.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@main_bp.route('/new')
def new_game():
    """Create a new puzzle and store it in the active game state."""
    clues_param = request.args.get('clues')
    difficulty = request.args.get('difficulty', 'medium')

    if clues_param is not None:
        try:
            clues = int(clues_param)
        except (TypeError, ValueError):
            return jsonify({'error': 'Clues must be an integer'}), 400

        if clues < 1:
            return jsonify({'error': 'Clues must be at least 1'}), 400
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
    else:
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    get_game_store().set_game(puzzle, solution)
    return jsonify({'puzzle': puzzle, 'solution': solution})


@main_bp.route('/check', methods=['POST'])
def check_solution():
    """Compare the submitted board against the active solution."""
    data = request.get_json(silent=True) or {}
    board = data.get('board')
    solution = get_game_store().get_solution()

    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for row_index in range(sudoku_logic.SIZE):
        for col_index in range(sudoku_logic.SIZE):
            if board[row_index][col_index] != solution[row_index][col_index]:
                incorrect.append([row_index, col_index])

    return jsonify({'incorrect': incorrect})
