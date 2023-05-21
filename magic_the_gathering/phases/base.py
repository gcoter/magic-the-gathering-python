from abc import abstractmethod
from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class Phase:
    def __init__(
        self,
        name: str,
    ):
        self.name = name

    @abstractmethod
    def run(self, game_state: GameState) -> GameState:
        raise NotImplementedError("This method must be implemented in a subclass.")
