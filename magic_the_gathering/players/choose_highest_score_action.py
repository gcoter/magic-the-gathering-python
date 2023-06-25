from abc import abstractmethod
from typing import List

import numpy as np

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.base import Player


class ChooseHighestScoreActionPlayer(Player):
    def _choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        action_scores = self._score_actions(game_state=game_state, actions=possible_actions)
        action_scores = self.softmax(action_scores)
        self.logger.debug(f"Action scores: {action_scores}")
        highest_score_action_index = np.random.choice(
            np.arange(len(possible_actions)), size=1, replace=False, p=action_scores
        )[0]
        return possible_actions[highest_score_action_index]

    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

    @abstractmethod
    def _score_actions(self, game_state: GameState, actions: List[Action]) -> np.ndarray:
        raise NotImplementedError
