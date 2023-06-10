from abc import abstractmethod
from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.base import Player


class ChooseHighestScoreActionPlayer(Player):
    def _choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        action_scores = [self._score_action(game_state, action) for action in possible_actions]
        highest_score_action_index = action_scores.index(max(action_scores))
        return possible_actions[highest_score_action_index]

    @abstractmethod
    def _score_action(self, game_state: GameState, action: Action) -> float:
        raise NotImplementedError
