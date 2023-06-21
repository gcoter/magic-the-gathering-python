from typing import Dict, List

import numpy as np
import torch

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.choose_highest_score_action import ChooseHighestScoreActionPlayer
from magic_the_gathering.players.deep_learning_based.models.base import BaseDeepLearningScorer


class DeepLearningBasedPlayer(ChooseHighestScoreActionPlayer):
    def __init__(
        self,
        index: int,
        life_points: int = 20,
        mana_pool: Dict[str, int] = None,
        is_alive: bool = True,
        scorer: BaseDeepLearningScorer = None,
    ):
        super().__init__(index=index, life_points=life_points, mana_pool=mana_pool, is_alive=is_alive)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scorer = scorer
        self.scorer.to(self.device)
        self.scorer.eval()

    def _score_actions(self, game_state: GameState, actions: List[Action]) -> np.ndarray:
        game_state_vectors = [game_state.to_vectors()] * len(actions)
        action_vectors = []
        for action in actions:
            if action is None:
                n_cards = len(game_state_vectors[0]["zones"])
                action_vectors.append(
                    {
                        "general": np.zeros(self.scorer.action_general_dim),
                        "source_card_uuids": np.zeros(n_cards),
                        "target_card_uuids": np.zeros(n_cards),
                    }
                )
            else:
                action_vectors.append(action.to_vectors(game_state=game_state))

        batch_game_state_vectors_torch = {
            "global": torch.tensor(np.array([game_state_vector["global"] for game_state_vector in game_state_vectors]))
            .float()
            .to(self.device),
            "players": torch.tensor(
                np.array([game_state_vector["players"] for game_state_vector in game_state_vectors])
            )
            .float()
            .to(self.device),
            "zones": torch.tensor(np.array([game_state_vector["zones"] for game_state_vector in game_state_vectors]))
            .float()
            .to(self.device),
        }
        batch_action_vectors_torch = {
            "general": torch.tensor(np.array([action_vector["general"] for action_vector in action_vectors]))
            .float()
            .to(self.device),
            "source_card_uuids": torch.tensor(
                np.array([action_vector["source_card_uuids"] for action_vector in action_vectors])
            )
            .bool()
            .to(self.device),
            "target_card_uuids": torch.tensor(
                np.array([action_vector["target_card_uuids"] for action_vector in action_vectors])
            )
            .bool()
            .to(self.device),
        }

        scores = (
            self.scorer(
                batch_game_state_vectors=batch_game_state_vectors_torch, batch_action_vectors=batch_action_vectors_torch
            )
            .cpu()
            .detach()
            .numpy()[:, 0]
        )

        return scores
