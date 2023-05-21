from abc import abstractmethod
from typing import Dict, List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class Player:
    def __init__(self, life_points: int = 20, mana_pool: Dict[str, int] = None, is_alive: bool = True):
        self.life_points = life_points
        self.mana_pool = mana_pool
        if self.mana_pool is None:
            self.mana_pool = {
                "white": 0,
                "blue": 0,
                "black": 0,
                "red": 0,
                "green": 0,
            }
        self.is_alive = is_alive  # FIXME: Maybe is_alive is just the same as life_points > 0?

    @abstractmethod
    def choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        raise NotImplementedError
