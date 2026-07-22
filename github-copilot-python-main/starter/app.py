"""Flask entry point for the Sudoku application."""

from flask import Flask

try:
    from .game_state import GameStore
    from .routes import main_bp
except ImportError:  # pragma: no cover - allows running the file directly
    from game_state import GameStore
    from routes import main_bp


# Keep a simple in-memory store for the active puzzle and solution.
CURRENT = {
    'puzzle': None,
    'solution': None,
}


def create_app() -> Flask:
    """Create and configure the Flask app instance."""
    app = Flask(__name__)
    app.extensions['game_store'] = GameStore(CURRENT)
    app.register_blueprint(main_bp)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)