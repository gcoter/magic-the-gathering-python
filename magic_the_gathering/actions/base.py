from abc import abstractmethod
from typing import List

from magic_the_gathering.game_state import GameState


class Action:
    @classmethod
    @abstractmethod
    def list_possible_actions(cls, game_state: GameState) -> List["Action"]:
        raise NotImplementedError

    def __init__(
        self,
        owner: str,
    ):
        self.owner = owner

    @abstractmethod
    def _execute(self, game_state: GameState) -> GameState:
        raise NotImplementedError

    def execute(self, game_state: GameState) -> GameState:
        game_state = self._execute(game_state)
        game_state.action_history.append(self)
        game_state.check_if_game_is_over()
        return game_state
