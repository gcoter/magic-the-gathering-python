from abc import abstractmethod
from typing import Dict, List

import numpy as np
import torch

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.deep_learning_based.base_scorer import BaseDeepLearningScorer
from magic_the_gathering.players.deep_learning_based.single_action_scorer.dataset import SingleActionScorerPreprocessor


class BaseSingleActionScorer(BaseDeepLearningScorer):
    def __init__(
        self,
        max_n_zone_vectors: int,
        zone_vector_dim: int,
        max_n_action_source_cards: int,
        max_n_action_target_cards: int,
        action_history_length: int = None,
    ):
        super().__init__()
        self.max_n_zone_vectors = max_n_zone_vectors
        self.zone_vector_dim = zone_vector_dim
        self.max_n_action_source_cards = max_n_action_source_cards
        self.max_n_action_target_cards = max_n_action_target_cards
        self.action_history_length = action_history_length
        self.preprocessor = SingleActionScorerPreprocessor(device=self.device)
        self.loss = torch.nn.BCELoss()

    def score_actions(self, game_state: GameState, actions: List[Action]) -> np.ndarray:
        game_state_vectors = game_state.to_vectors()
        preprocessed_game_state_vectors = self.preprocessor.preprocess_game_state_vectors(
            game_state_vectors=game_state_vectors,
            max_n_zone_vectors=self.max_n_zone_vectors,
            zone_vector_dim=self.zone_vector_dim,
        )

        preprocessed_action_vectors_history = None
        if self.action_history_length is not None:
            action_vectors_history = Action.HISTORY[-self.action_history_length :]
            preprocessed_action_vectors_history = self.preprocessor.preprocess_action_vectors_history(
                action_vectors_history=action_vectors_history,
                max_n_zone_vectors=self.max_n_zone_vectors,
                zone_vector_dim=self.zone_vector_dim,
                max_n_action_source_cards=self.max_n_action_source_cards,
                max_n_action_target_cards=self.max_n_action_target_cards,
            )

        batch_preprocessed_game_state_vectors = []
        batch_preprocessed_action_vectors_history = None
        batch_preprocessed_action_vectors = []
        for action in actions:
            action_vectors = action.to_vectors(game_state=game_state)
            preprocessed_action_vectors = self.preprocessor.preprocess_action_vectors(
                action_vectors=action_vectors,
                max_n_zone_vectors=self.max_n_zone_vectors,
                zone_vector_dim=self.zone_vector_dim,
                max_n_action_source_cards=self.max_n_action_source_cards,
                max_n_action_target_cards=self.max_n_action_target_cards,
            )
            batch_preprocessed_game_state_vectors.append(preprocessed_game_state_vectors)
            if preprocessed_action_vectors_history is not None:
                if batch_preprocessed_action_vectors_history is None:
                    batch_preprocessed_action_vectors_history = []
                batch_preprocessed_action_vectors_history.append(preprocessed_action_vectors_history)
            batch_preprocessed_action_vectors.append(preprocessed_action_vectors)
        batch_preprocessed_game_state_vectors = self.__concat_across_keys(batch_preprocessed_game_state_vectors)
        if batch_preprocessed_action_vectors_history is not None:
            batch_preprocessed_action_vectors_history = self.__concat_across_list_keys(
                batch_preprocessed_action_vectors_history
            )
        batch_preprocessed_action_vectors = self.__concat_across_keys(batch_preprocessed_action_vectors)

        scores = self.forward(
            batch_preprocessed_game_state_vectors=batch_preprocessed_game_state_vectors,
            batch_preprocessed_action_vectors_history=batch_preprocessed_action_vectors_history,
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

    def __concat_across_list_keys(
        self, list_of_list_of_dict_of_tensors: List[List[Dict[str, torch.Tensor]]]
    ) -> List[Dict[str, torch.Tensor]]:
        concatenated_list_of_dict = [{} for _ in range(len(list_of_list_of_dict_of_tensors[0]))]
        for list_of_dict_of_tensors in list_of_list_of_dict_of_tensors:
            for index, dict_of_tensors in enumerate(list_of_dict_of_tensors):
                concatenated_dict = concatenated_list_of_dict[index]
                for key, tensor in dict_of_tensors.items():
                    if key not in concatenated_dict:
                        concatenated_dict[key] = []
                    concatenated_dict[key].append(tensor[None])  # Add one dimension for batch

        for concatenated_dict in concatenated_list_of_dict:
            for key, tensors in concatenated_dict.items():
                if isinstance(tensors, list):
                    concatenated_dict[key] = torch.cat(tensors, dim=0).to(self.device)

        return concatenated_list_of_dict

    @abstractmethod
    def forward(
        self,
        batch_preprocessed_game_state_vectors: Dict[str, torch.Tensor],
        batch_preprocessed_action_vectors: Dict[str, torch.Tensor],
        batch_preprocessed_action_vectors_history: List[Dict[str, torch.Tensor]] = None,
    ):
        """
        Inputs:

        - batch_preprocessed_game_state_vectors:

        {
            "global": (batch_size, global_game_state_dim),
            "players": (batch_size, n_players, player_dim),
            "zones": (batch_size, n_cards, zone_vector_dim),
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

        - (Optional) batch_preprocessed_action_vectors_history:

        [
            {
                "general": (batch_size, action_general_dim),
                "source_card_uuids": (batch_size, n_cards),
                "source_card_uuids_padding_mask": (batch_size, n_cards),
                "target_card_uuids": (batch_size, n_cards),
                "target_card_uuids_padding_mask": (batch_size, n_cards)
            }
        ] * action_history_length

        Outputs:
        - scores: (batch_size,)
        """
        raise NotImplementedError

    def __step(self, batch, batch_idx, base_metric_name):
        if self.action_history_length is None:
            batch_preprocessed_game_state_vectors, batch_preprocessed_action_vectors, batch_labels = batch
            batch_predicted_scores = self.forward(
                batch_preprocessed_game_state_vectors=batch_preprocessed_game_state_vectors,
                batch_preprocessed_action_vectors=batch_preprocessed_action_vectors,
            )
        else:
            (
                batch_preprocessed_game_state_vectors,
                batch_preprocessed_action_vectors_history,
                batch_preprocessed_action_vectors,
                batch_labels,
            ) = batch
            batch_predicted_scores = self.forward(
                batch_preprocessed_game_state_vectors=batch_preprocessed_game_state_vectors,
                batch_preprocessed_action_vectors_history=batch_preprocessed_action_vectors_history,
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
