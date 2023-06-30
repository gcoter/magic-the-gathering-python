from abc import abstractmethod
from typing import Dict, List

import numpy as np
import torch

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.deep_learning_based.base_scorer import BaseDeepLearningScorer
from magic_the_gathering.players.deep_learning_based.single_action_scorer.dataset import SingleActionScorerPreprocessor


class BaseSingleActionScorer(BaseDeepLearningScorer):
    def __init__(self, max_n_cards: int):
        super().__init__()
        self.max_n_cards = max_n_cards
        self.loss = torch.nn.BCELoss()
        self.preprocessor = SingleActionScorerPreprocessor(device=self.device)

    def score_actions(self, game_state: GameState, actions: List[Action]) -> np.ndarray:
        game_state_vectors = game_state.to_vectors()
        preprocessed_game_state_vectors = self.preprocessor.preprocess_game_state_vectors(
            game_state_vectors=game_state_vectors, max_n_cards=self.max_n_cards
        )
        batch_preprocessed_game_state_vectors = []
        batch_preprocessed_action_vectors = []
        for action in actions:
            action_vectors = action.to_vectors(game_state=game_state)
            preprocessed_action_vectors = self.preprocessor.preprocess_action_vectors(
                action_vectors=action_vectors, max_n_cards=self.max_n_cards
            )
            batch_preprocessed_game_state_vectors.append(preprocessed_game_state_vectors)
            batch_preprocessed_action_vectors.append(preprocessed_action_vectors)
        batch_preprocessed_game_state_vectors = self.__concat_across_keys(batch_preprocessed_game_state_vectors)
        batch_preprocessed_action_vectors = self.__concat_across_keys(batch_preprocessed_action_vectors)

        scores = self.forward(
            batch_preprocessed_game_state_vectors=batch_preprocessed_game_state_vectors,
            batch_preprocessed_action_vectors=batch_preprocessed_action_vectors,
        )
        scores = torch.nn.functional.softmax(scores, dim=0)
        return scores.cpu().detach().numpy()

    def __concat_across_keys(self, list_of_dict_of_tensors: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        concatenated_dict = {}
        for dict_of_tensors in list_of_dict_of_tensors:
            for key, tensor in dict_of_tensors.items():
                if key not in concatenated_dict:
                    concatenated_dict[key] = []
                concatenated_dict[key].append(tensor[None])  # Add one dimension for batch

        for key, tensors in concatenated_dict.items():
            concatenated_dict[key] = torch.cat(tensors, dim=0).to(self.device)

        return concatenated_dict

    @abstractmethod
    def forward(
        self,
        batch_preprocessed_game_state_vectors: Dict[str, torch.Tensor],
        batch_preprocessed_action_vectors: Dict[str, torch.Tensor],
    ):
        """
        Inputs:

        - batch_preprocessed_game_state_vectors:

        {
            "global": (batch_size, global_game_state_dim),
            "players": (batch_size, n_players, player_dim),
            "zones": (batch_size, n_cards, card_dim),
            "zones_padding_mask": (batch_size, n_cards)
        }

        - batch_preprocessed_action_vectors:

        {
            "general": (batch_size, action_general_dim),
            "source_card_uuids": (batch_size, n_cards),
            "source_card_uuids_padding_mask": (batch_size, n_cards),
            "target_card_uuids": (batch_size, n_cards),
            "target_card_uuids_padding_mask": (batch_size, n_cards)
        }

        Outputs:
        - scores: (batch_size,)
        """
        raise NotImplementedError

    def __step(self, batch, batch_idx, base_metric_name):
        batch_preprocessed_game_state_vectors, batch_preprocessed_action_vectors, batch_labels = batch
        batch_predicted_scores = self.forward(
            batch_preprocessed_game_state_vectors=batch_preprocessed_game_state_vectors,
            batch_preprocessed_action_vectors=batch_preprocessed_action_vectors,
        )
        batch_loss = self.loss(batch_predicted_scores, batch_labels)
        self.log(f"{base_metric_name}_loss", batch_loss, on_epoch=True, prog_bar=True)
        return batch_loss

    def training_step(self, batch, batch_idx):
        return self.__step(batch=batch, batch_idx=batch_idx, base_metric_name="training")

    def validation_step(self, batch, batch_idx):
        return self.__step(batch=batch, batch_idx=batch_idx, base_metric_name="validation")

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        batch_preprocessed_game_state_vectors, batch_preprocessed_action_vectors = batch
        batch_predicted_scores = self.forward(
            batch_preprocessed_game_state_vectors=batch_preprocessed_game_state_vectors,
            batch_preprocessed_action_vectors=batch_preprocessed_action_vectors,
        )
        return batch_predicted_scores

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters())

    def get_n_parameters(self):
        return sum(p.numel() for p in self.parameters())
