import logging
from abc import abstractmethod

from magic_the_gathering.game_state import GameState


class Phase:
    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _run(self, game_state: GameState) -> GameState:
        raise NotImplementedError("This method must be implemented in a subclass.")

    def run(self, game_state: GameState) -> GameState:
        self.logger.info(f"===== {self.name} =====")
        game_state = self._run(game_state)
        game_state = self.__empty_mana_pool(game_state=game_state)
        return game_state

    def __empty_mana_pool(self, game_state: GameState):
        for player_index in range(game_state.n_players):
            game_state.players[player_index].mana_pool = {
                "W": 0,
                "U": 0,
                "B": 0,
                "R": 0,
                "G": 0,
                "any": 0,
            }
        return game_state
