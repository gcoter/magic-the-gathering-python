from abc import abstractmethod

from magic_the_gathering.game_state import GameState


class Phase:
    def __init__(
        self,
        name: str,
        allows_sorcery_speed_when_stack_is_empty: bool = False,
        players_get_priority: bool = True,
    ):
        self.name = name
        self.allows_sorcery_speed_when_stack_is_empty = allows_sorcery_speed_when_stack_is_empty
        self.players_get_priority = players_get_priority

    @abstractmethod
    def run(self, game_state: GameState) -> GameState:
        raise NotImplementedError("This method must be implemented in a subclass.")
