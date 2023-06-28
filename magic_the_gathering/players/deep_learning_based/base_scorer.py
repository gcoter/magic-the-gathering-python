from abc import abstractmethod
from typing import List

import numpy as np
from pytorch_lightning import LightningModule

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class BaseDeepLearningScorer(LightningModule):
    @abstractmethod
    def score_actions(self, game_state: GameState, actions: List[Action]) -> np.ndarray:
        pass
