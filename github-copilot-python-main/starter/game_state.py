"""Simple in-memory game state helpers for the Sudoku Flask app."""

from typing import Any, Dict, List, Optional

Board = List[List[int]]


class GameStore:
    """Keep the current puzzle and solution in memory for the active game."""

    def __init__(self, storage: Dict[str, Any]):
        self.storage = storage

    def set_game(self, puzzle: Optional[Board], solution: Optional[Board]) -> None:
        """Store the current puzzle and solution."""
        self.storage['puzzle'] = puzzle
        self.storage['solution'] = solution

    def clear(self) -> None:
        """Remove the current game state."""
        self.set_game(None, None)

    def get_solution(self) -> Optional[Board]:
        """Return the active solution if one exists."""
        return self.storage.get('solution')
