import logging
from abc import abstractmethod
from typing import Dict, List

import numpy as np

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class Player:
    def __init__(self, index: int, life_points: int = 20, mana_pool: Dict[str, int] = None, is_alive: bool = True):
        self.index = index
        self.life_points = life_points
        self.mana_pool = mana_pool
        if self.mana_pool is None:
            self.mana_pool = {
                "W": 0,
                "U": 0,
                "B": 0,
                "R": 0,
                "G": 0,
            }
        self.is_alive = is_alive  # FIXME: Maybe is_alive is just the same as life_points > 0?
        self.logger = logging.getLogger(self.__class__.__name__)

        self.dataset = []

    @abstractmethod
    def _choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        raise NotImplementedError

    def choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        self.logger.debug(f"{self} is choosing an action among: {possible_actions}")
        action = self._choose_action(game_state, possible_actions)
        self.dataset.append(
            {
                "action_history": Action.HISTORY[-10:],
                "current_game_state": game_state.to_vectors(),
                "possible_actions": [action.to_vectors(game_state=game_state) for action in possible_actions],
                "chosen_action_index": possible_actions.index(action),
            }
        )
        self.logger.debug(f"Chosen action: {action}")
        return action

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(life_points={self.life_points}, mana_pool={self.mana_pool})"

    def to_json_dict(self) -> Dict:
        return {
            "index": self.index,
            "life_points": self.life_points,
            "mana_pool": self.mana_pool,
            "is_alive": self.is_alive,
        }

    def to_vector(self) -> np.ndarray:
        return np.array(
            [
                self.life_points,
                self.mana_pool["W"],
                self.mana_pool["U"],
                self.mana_pool["B"],
                self.mana_pool["R"],
                self.mana_pool["G"],
                self.is_alive,
            ]
        )
