from typing import Dict, List, Tuple

import numpy as np
import torch

from magic_the_gathering.game_logs_dataset import GameLogsDataset


class SingleActionScorerPreprocessor:
    def __init__(self, device):
        self.device = device

    def preprocess(
        self,
        game_state_vectors: Dict[str, np.ndarray],
        action_vectors: Dict[str, np.ndarray],
        max_n_zone_vectors: int,
        zone_vector_dim: int,
        max_n_action_source_cards: int,
        max_n_action_target_cards: int,
        action_vectors_history: List[Dict[str, np.ndarray]] = None,
    ) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]:
        preprocessed_game_state_vectors = self.preprocess_game_state_vectors(
            game_state_vectors, max_n_zone_vectors=max_n_zone_vectors, zone_vector_dim=zone_vector_dim
        )
        preprocessed_action_vectors = self.preprocess_action_vectors(
            action_vectors,
            max_n_zone_vectors=max_n_zone_vectors,
            zone_vector_dim=zone_vector_dim,
            max_n_action_source_cards=max_n_action_source_cards,
            max_n_action_target_cards=max_n_action_target_cards,
        )
        if action_vectors_history is None:
            return preprocessed_game_state_vectors, preprocessed_action_vectors
        preprocessed_action_vectors_history = self.preprocess_action_vectors_history(
            action_vectors_history=action_vectors_history,
            max_n_zone_vectors=max_n_zone_vectors,
            zone_vector_dim=zone_vector_dim,
            max_n_action_source_cards=max_n_action_source_cards,
            max_n_action_target_cards=max_n_action_target_cards,
        )
        return preprocessed_game_state_vectors, preprocessed_action_vectors_history, preprocessed_action_vectors

    def preprocess_game_state_vectors(
        self,
        game_state_vectors: Dict[str, np.ndarray],
        max_n_zone_vectors: int,
        zone_vector_dim: int,
    ) -> Dict[str, torch.Tensor]:
        zones_vectors = game_state_vectors["zones"]
        padded_zones_vectors, zones_padding_mask = self.__pad_2_dim_vectors(
            zones_vectors, target_dim_0=max_n_zone_vectors, target_dim_1=zone_vector_dim
        )
        return {
            "global": torch.from_numpy(game_state_vectors["global"]).float().to(self.device),
            "players": torch.from_numpy(game_state_vectors["players"]).float().to(self.device),
            "zones": torch.from_numpy(padded_zones_vectors).float().to(self.device),
            "zones_padding_mask": torch.from_numpy(zones_padding_mask).bool().to(self.device),
        }

    def preprocess_action_vectors_history(
        self,
        action_vectors_history: List[Dict[str, np.ndarray]],
        max_n_zone_vectors: int,
        zone_vector_dim: int,
        max_n_action_source_cards: int,
        max_n_action_target_cards: int,
    ):
        return [
            self.preprocess_action_vectors(
                action_vectors=action_vectors,
                max_n_zone_vectors=max_n_zone_vectors,
                zone_vector_dim=zone_vector_dim,
                max_n_action_source_cards=max_n_action_source_cards,
                max_n_action_target_cards=max_n_action_target_cards,
            )
            for action_vectors in action_vectors_history
        ]

    def preprocess_action_vectors(
        self,
        action_vectors: Dict[str, np.ndarray],
        max_n_zone_vectors: int,
        zone_vector_dim: int,
        max_n_action_source_cards: int,
        max_n_action_target_cards: int,
    ) -> Dict[str, torch.Tensor]:
        source_card_vectors = action_vectors["source_card_vectors"]
        padded_source_card_vectors, source_card_vectors_padding_mask = self.__pad_2_dim_vectors(
            source_card_vectors, target_dim_0=max_n_action_source_cards, target_dim_1=zone_vector_dim
        )

        source_card_uuids = action_vectors["source_card_uuids"]
        padded_source_card_uuids, source_card_uuids_padding_mask = self.__pad_1_dim_vectors(
            source_card_uuids, target_dim_0=max_n_zone_vectors
        )

        target_card_vectors = action_vectors["target_card_vectors"]
        padded_target_card_vectors, target_card_vectors_padding_mask = self.__pad_2_dim_vectors(
            target_card_vectors, target_dim_0=max_n_action_target_cards, target_dim_1=zone_vector_dim
        )

        target_card_uuids = action_vectors["target_card_uuids"]
        padded_target_card_uuids, target_card_uuids_padding_mask = self.__pad_1_dim_vectors(
            target_card_uuids, target_dim_0=max_n_zone_vectors
        )

        return {
            "general": torch.from_numpy(action_vectors["general"]).float().to(self.device),
            "source_card_vectors": torch.from_numpy(padded_source_card_vectors).float().to(self.device),
            "source_card_vectors_padding_mask": torch.from_numpy(source_card_vectors_padding_mask)
            .bool()
            .to(self.device),
            "source_card_uuids": torch.from_numpy(padded_source_card_uuids).bool().to(self.device),
            "source_card_uuids_padding_mask": torch.from_numpy(source_card_uuids_padding_mask).bool().to(self.device),
            "target_card_vectors": torch.from_numpy(padded_target_card_vectors).float().to(self.device),
            "target_card_vectors_padding_mask": torch.from_numpy(target_card_vectors_padding_mask)
            .bool()
            .to(self.device),
            "target_card_uuids": torch.from_numpy(padded_target_card_uuids).bool().to(self.device),
            "target_card_uuids_padding_mask": torch.from_numpy(target_card_uuids_padding_mask).bool().to(self.device),
        }

    def __pad_1_dim_vectors(self, vectors: np.ndarray, target_dim_0: int):
        if len(vectors) == 0:
            padded_vectors = np.zeros(target_dim_0)
            padding_mask = np.ones(target_dim_0)
            return padded_vectors, padding_mask
        if len(vectors) < target_dim_0:
            pad_width = ((0, target_dim_0 - len(vectors)),)
            padding_mask = np.zeros(target_dim_0)
            padding_mask[: len(vectors)] = 1
            padded_vectors = np.pad(vectors, pad_width=pad_width)
            return padded_vectors, padding_mask
        else:
            padded_vectors = vectors[:target_dim_0]
            padding_mask = np.zeros(target_dim_0)
            return padded_vectors, padding_mask

    def __pad_2_dim_vectors(self, vectors: np.ndarray, target_dim_0: int, target_dim_1: int):
        if len(vectors) == 0:
            padded_vectors = np.zeros(shape=(target_dim_0, target_dim_1))
            padding_mask = np.ones(target_dim_0)
            return padded_vectors, padding_mask
        assert len(vectors.shape) == 2
        assert vectors.shape[1] == target_dim_1
        if len(vectors) < target_dim_0:
            pad_width = ((0, target_dim_0 - len(vectors)), (0, 0))
            padding_mask = np.zeros(target_dim_0)
            padding_mask[: len(vectors)] = 1
            padded_vectors = np.pad(vectors, pad_width=pad_width)
            return padded_vectors, padding_mask
        else:
            padded_vectors = vectors[:target_dim_0]
            padding_mask = np.zeros(target_dim_0)
            return padded_vectors, padding_mask


class SingleActionScorerDataset(torch.utils.data.Dataset):
    def __init__(
        self,
        device,
        max_n_zone_vectors: int,
        zone_vector_dim: int,
        max_n_action_source_cards: int,
        max_n_action_target_cards: int,
        game_logs_dataset: GameLogsDataset,
        return_label: bool = False,
        action_history_length: int = None,
    ):
        self.device = device
        self.game_logs_dataset = game_logs_dataset
        self.return_label = return_label
        self.action_history_length = action_history_length
        self.index_df = self.game_logs_dataset.get_index()
        self.max_n_zone_vectors = max_n_zone_vectors
        self.zone_vector_dim = zone_vector_dim
        self.max_n_action_source_cards = max_n_action_source_cards
        self.max_n_action_target_cards = max_n_action_target_cards
        self.preprocessor = SingleActionScorerPreprocessor(device=self.device)

    def __len__(self) -> int:
        return len(self.index_df)

    def __getitem__(self, idx: int):
        game_id = self.index_df.iloc[idx]["game_id"]
        item_index = self.index_df.iloc[idx]["item_index"]
        item_dict = self.game_logs_dataset.get_item(game_id=game_id, item_index=item_index)
        game_state_vectors = item_dict["game_state"]
        chosen_action_index = item_dict["chosen_action_index"]
        chosen_action_vectors = item_dict["possible_actions"][chosen_action_index]

        action_vectors_history = None
        if self.action_history_length is not None:
            action_history = self.game_logs_dataset.get_action_history(game_id=game_id)
            end_action_history_index = item_dict["action_history_index"]
            start_action_history_index = max(0, end_action_history_index - self.action_history_length)
            action_vectors_history = action_history[start_action_history_index:end_action_history_index]

        if action_vectors_history is None:
            preprocessed_action_vectors_history = None
            preprocessed_game_state_vectors, preprocessed_action_vectors = self.preprocessor.preprocess(
                game_state_vectors=game_state_vectors,
                action_vectors=chosen_action_vectors,
                max_n_zone_vectors=self.max_n_zone_vectors,
                zone_vector_dim=self.zone_vector_dim,
                max_n_action_source_cards=self.max_n_action_source_cards,
                max_n_action_target_cards=self.max_n_action_target_cards,
                action_vectors_history=action_vectors_history,
            )
        else:
            (
                preprocessed_game_state_vectors,
                preprocessed_action_vectors_history,
                preprocessed_action_vectors,
            ) = self.preprocessor.preprocess(
                game_state_vectors=game_state_vectors,
                action_vectors=chosen_action_vectors,
                max_n_zone_vectors=self.max_n_zone_vectors,
                zone_vector_dim=self.zone_vector_dim,
                max_n_action_source_cards=self.max_n_action_source_cards,
                max_n_action_target_cards=self.max_n_action_target_cards,
                action_vectors_history=action_vectors_history,
            )

        label = None

        if self.return_label:
            winner_player_index = self.game_logs_dataset.get_winner_player_index(game_id=game_id)
            label = self.__get_label(
                chosen_action_vectors=chosen_action_vectors, winner_player_index=winner_player_index
            )

        if preprocessed_action_vectors_history is None:
            if label is not None:
                return preprocessed_game_state_vectors, preprocessed_action_vectors, label
            return preprocessed_game_state_vectors, preprocessed_action_vectors
        else:
            if label is not None:
                return (
                    preprocessed_game_state_vectors,
                    preprocessed_action_vectors_history,
                    preprocessed_action_vectors,
                    label,
                )
            return preprocessed_game_state_vectors, preprocessed_action_vectors_history, preprocessed_action_vectors

    def __get_label(self, chosen_action_vectors: Dict, winner_player_index: int) -> torch.Tensor:
        source_player_index = chosen_action_vectors["source_player_index"]
        assert source_player_index is not None
        label = np.array(source_player_index == winner_player_index)
        return torch.from_numpy(label).float().to(self.device)
