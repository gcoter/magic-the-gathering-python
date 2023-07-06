from typing import Dict, List

import numpy as np
import torch

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_logs_dataset import GameLogsDataset
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.deep_learning_based.base_scorer import BaseDeepLearningScorer
from magic_the_gathering.players.sample_action_from_scores import SampleActionFromScoresPlayer


class DeepLearningBasedPlayer(SampleActionFromScoresPlayer):
    def __init__(
        self,
        index: int,
        life_points: int = 20,
        mana_pool: Dict[str, int] = None,
        is_alive: bool = True,
        game_logs_dataset: GameLogsDataset = None,
        scorer: BaseDeepLearningScorer = None,
    ):
        super().__init__(
            index=index,
            life_points=life_points,
            mana_pool=mana_pool,
            is_alive=is_alive,
            game_logs_dataset=game_logs_dataset,
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scorer = scorer
        self.scorer.to(self.device)
        self.scorer.eval()

    def _score_actions(self, game_state: GameState, actions: List[Action]) -> np.ndarray:
        return self.scorer.score_actions(game_state=game_state, actions=actions)
