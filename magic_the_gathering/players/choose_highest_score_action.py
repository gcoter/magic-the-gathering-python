from abc import abstractmethod
from typing import List

import numpy as np

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.base import Player


class ChooseHighestScoreActionPlayer(Player):
    def _choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        action_scores = self._score_actions(game_state=game_state, actions=possible_actions)
        self.logger.debug(f"Action scores: {action_scores}")
        highest_score_action_index = np.argmax(action_scores)
        return possible_actions[highest_score_action_index]

    @abstractmethod
    def _score_actions(self, game_state: GameState, actions: List[Action]) -> np.ndarray:
        raise NotImplementedError
