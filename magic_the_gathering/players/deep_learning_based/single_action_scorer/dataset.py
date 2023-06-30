from typing import Dict, Tuple

import numpy as np
import torch

from magic_the_gathering.game_logs_dataset import GameLogsDataset


class SingleActionScorerPreprocessor:
    def __init__(self, device):
        self.device = device

    def preprocess(
        self, game_state_vectors: Dict[str, np.ndarray], action_vectors: Dict[str, np.ndarray], max_n_cards: int
    ) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]:
        preprocessed_game_state_vectors = self.preprocess_game_state_vectors(
            game_state_vectors, max_n_cards=max_n_cards
        )
        preprocessed_action_vectors = self.preprocess_action_vectors(action_vectors, max_n_cards=max_n_cards)
        return preprocessed_game_state_vectors, preprocessed_action_vectors

    def preprocess_game_state_vectors(
        self, game_state_vectors: Dict[str, np.ndarray], max_n_cards: int
    ) -> Dict[str, torch.Tensor]:
        zones_vectors = game_state_vectors["zones"]
        padded_zones_vectors, zones_padding_mask = self.__pad_to_max_zone_length(zones_vectors, max_n_cards=max_n_cards)
        return {
            "global": torch.from_numpy(game_state_vectors["global"]).float().to(self.device),
            "players": torch.from_numpy(game_state_vectors["players"]).float().to(self.device),
            "zones": torch.from_numpy(padded_zones_vectors).float().to(self.device),
            "zones_padding_mask": torch.from_numpy(zones_padding_mask).bool().to(self.device),
        }

    def preprocess_action_vectors(
        self, action_vectors: Dict[str, np.ndarray], max_n_cards: int
    ) -> Dict[str, torch.Tensor]:
        source_card_uuids = action_vectors["source_card_uuids"]
        padded_source_card_uuids, source_card_uuids_padding_mask = self.__pad_to_max_zone_length(
            source_card_uuids, max_n_cards=max_n_cards
        )

        target_card_uuids = action_vectors["target_card_uuids"]
        padded_target_card_uuids, target_card_uuids_padding_mask = self.__pad_to_max_zone_length(
            target_card_uuids, max_n_cards=max_n_cards
        )

        return {
            "general": torch.from_numpy(action_vectors["general"]).float().to(self.device),
            "source_card_uuids": torch.from_numpy(padded_source_card_uuids).bool().to(self.device),
            "source_card_uuids_padding_mask": torch.from_numpy(source_card_uuids_padding_mask).bool().to(self.device),
            "target_card_uuids": torch.from_numpy(padded_target_card_uuids).bool().to(self.device),
            "target_card_uuids_padding_mask": torch.from_numpy(target_card_uuids_padding_mask).bool().to(self.device),
        }

    def __pad_to_max_zone_length(self, vectors: np.ndarray, max_n_cards: int) -> Tuple[np.ndarray, np.ndarray]:
        assert len(vectors) > 0
        assert max_n_cards >= len(vectors)
        padding_mask = np.zeros(max_n_cards)
        padding_mask[: len(vectors)] = 1
        if len(vectors.shape) == 1:
            pad_width = ((0, max_n_cards - len(vectors)),)
        elif len(vectors.shape) == 2:
            pad_width = ((0, max_n_cards - len(vectors)), (0, 0))
        else:
            raise ValueError(f"Invalid vector shape: {vectors.shape}")
        padded_vectors = np.pad(vectors, pad_width=pad_width)
        return padded_vectors, padding_mask


class SingleActionScorerDataset(torch.utils.data.Dataset):
    def __init__(self, device, max_n_cards: int, game_logs_dataset: GameLogsDataset, return_label: bool = False):
        self.device = device
        self.game_logs_dataset = game_logs_dataset
        self.return_label = return_label
        self.index_df = self.game_logs_dataset.get_index()
        self.max_n_cards = max_n_cards
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

        preprocessed_game_state_vectors, preprocessed_action_vectors = self.preprocessor.preprocess(
            game_state_vectors=game_state_vectors, action_vectors=chosen_action_vectors, max_n_cards=self.max_n_cards
        )

        if self.return_label:
            winner_player_index = self.game_logs_dataset.get_winner_player_index(game_id=game_id)
            label = self.__get_label(
                chosen_action_vectors=chosen_action_vectors, winner_player_index=winner_player_index
            )
            return preprocessed_game_state_vectors, preprocessed_action_vectors, label
        return preprocessed_game_state_vectors, preprocessed_action_vectors

    def __get_label(self, chosen_action_vectors: Dict, winner_player_index: int) -> torch.Tensor:
        source_player_index = chosen_action_vectors["source_player_index"]
        assert source_player_index is not None
        label = np.array(source_player_index == winner_player_index)
        return torch.from_numpy(label).float().to(self.device)
