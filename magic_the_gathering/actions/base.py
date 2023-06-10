import logging
from abc import abstractmethod
from typing import Dict, List

import numpy as np

from magic_the_gathering.game_state import GameState, ZonePosition


class Action:
    GLOBAL_ACTION_COUNT = 0
    DATASET = []

    @classmethod
    @abstractmethod
    def list_possible_actions(cls, game_state: GameState) -> List["Action"]:
        raise NotImplementedError

    def __init__(
        self,
        source_player_index: int = None,
        target_player_index: int = None,
        source_card_uuids: List[str] = None,
        target_card_uuids: List[str] = None,
        source_zone: ZonePosition = None,
        target_zone: ZonePosition = None,
    ):
        self.source_player_index = source_player_index
        self.target_player_index = target_player_index
        self.source_card_uuids = source_card_uuids
        self.target_card_uuids = target_card_uuids
        self.source_zone = source_zone
        self.target_zone = target_zone
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _execute(self, game_state: GameState) -> GameState:
        raise NotImplementedError

    def execute(self, game_state: GameState) -> GameState:
        self.logger.debug(f"Executing action: {self}")
        Action.DATASET.append({"game_state": game_state.to_json_dict(), "action": self.to_json_dict()})
        game_state = self._execute(game_state)
        Action.GLOBAL_ACTION_COUNT += 1
        game_state.check_if_game_is_over()
        return game_state

    def __str__(self) -> str:
        string = f"{self.__class__.__name__}("
        attribute_strings = [
            f"{attribute_name}={attribute_value}"
            for attribute_name, attribute_value in self.__dict__.items()
            if attribute_name != "logger"
        ]
        string += ", ".join(attribute_strings)
        string += ")"
        return string

    def __repr__(self) -> str:
        return self.__str__()

    def to_json_dict(self) -> dict:
        return {
            "action_type": self.__class__.__name__,
            "action_attributes": {
                attribute_name: attribute_value
                for attribute_name, attribute_value in self.__dict__.items()
                if attribute_name != "logger"
            },
        }

    def to_vectors(self, game_state: GameState) -> Dict[str, np.ndarray]:
        source_player_one_hot_vector = game_state.player_index_to_one_hot_vector(self.source_player_index)
        target_player_one_hot_vector = game_state.player_index_to_one_hot_vector(self.target_player_index)
        source_card_uuids_multi_hot_vector = game_state.card_uuids_to_multi_hot_vector(self.source_card_uuids)
        target_card_uuids_multi_hot_vector = game_state.card_uuids_to_multi_hot_vector(self.target_card_uuids)
        source_zone_one_hot_vector = game_state.zone_position_to_one_hot_vector(self.source_zone)
        target_zone_one_hot_vector = game_state.zone_position_to_one_hot_vector(self.target_zone)

        general_vector = np.concatenate(
            [
                source_player_one_hot_vector,
                target_player_one_hot_vector,
                source_zone_one_hot_vector,
                target_zone_one_hot_vector,
            ]
        )

        return {
            "general": general_vector,
            "source_card_uuids": source_card_uuids_multi_hot_vector,
            "target_card_uuids": target_card_uuids_multi_hot_vector,
        }
