from abc import abstractmethod

from magic_the_gathering.game_state import GameState


class Action:
    def __init__(
        self,
        owner: str,
    ):
        self.owner = owner

    @abstractmethod
    def execute(self, game_state: GameState) -> GameState:
        raise NotImplementedError
