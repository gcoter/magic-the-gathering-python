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
        return game_state
