from abc import abstractmethod
from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class PhaseWherePlayersGetPriority(Phase):
    @staticmethod
    @abstractmethod
    def list_possible_actions(game_state: GameState) -> List[Action]:
        raise NotImplementedError

    def __init__(
        self,
        name: str,
        allows_sorcery_speed_when_stack_is_empty: bool = False,
    ):
        super().__init__(name=name)
        self.allows_sorcery_speed_when_stack_is_empty = allows_sorcery_speed_when_stack_is_empty
