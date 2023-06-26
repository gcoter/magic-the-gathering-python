import logging
from abc import abstractmethod
from typing import Dict, List

import numpy as np

from magic_the_gathering.game_state import GameState, ZonePosition


class Action:
    HISTORY = []

    @staticmethod
    def type_to_one_hot_vector(action_type: str) -> np.ndarray:
        all_action_types = [
            "NoneAction",
            "CastCardAction",
            "DealDamageAction",
            "DeclareAttackerAction",
            "DeclareBlockerAction",
            "DrawAction",
            "KillPlayerAction",
            "MoveToGraveyardAction",
            "PassToNextPlayerAction",
            "PlayLandAction",
            "ResolveTopOfStackAction",
            "ShuffleAction",
            "TapAction",
            "UntapAction",
            "UntapAllAction",
        ]
        action_type_index = all_action_types.index(action_type)
        one_hot_vector = np.zeros(len(all_action_types))
        one_hot_vector[action_type_index] = 1
        return one_hot_vector

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
        Action.HISTORY.append(self.to_vectors(game_state=game_state))
        game_state = self._execute(game_state)
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
        source_zone_one_hot_vector = game_state.zone_position_to_one_hot_vector(self.source_zone)
        target_zone_one_hot_vector = game_state.zone_position_to_one_hot_vector(self.target_zone)

        general_vector = np.concatenate(
            [
                Action.type_to_one_hot_vector(self.__class__.__name__),
                source_player_one_hot_vector,
                target_player_one_hot_vector,
                source_zone_one_hot_vector,
                target_zone_one_hot_vector,
            ]
        ).astype(np.float32)

        zones_vector, uuids = game_state.zones_to_vector(return_uuids=True)
        source_card_vectors = []
        target_card_vectors = []
        if self.source_card_uuids is not None:
            for source_card_uuid in self.source_card_uuids:
                source_card_index = uuids.index(source_card_uuid)
                source_card_vector = zones_vector[source_card_index]
                source_card_vectors.append(source_card_vector)
        if self.target_card_uuids is not None:
            for target_card_uuid in self.target_card_uuids:
                target_card_index = uuids.index(target_card_uuid)
                target_card_vector = zones_vector[target_card_index]
                target_card_vectors.append(target_card_vector)

        source_card_vectors = np.array(source_card_vectors, dtype=np.float32)
        target_card_vectors = np.array(target_card_vectors, dtype=np.float32)

        source_card_uuids_multi_hot_vector = self.__card_uuids_to_multi_hot_vector(
            all_uuids=uuids, card_uuids=self.source_card_uuids
        )
        target_card_uuids_multi_hot_vector = self.__card_uuids_to_multi_hot_vector(
            all_uuids=uuids, card_uuids=self.target_card_uuids
        )

        return {
            "source_player_index": self.source_player_index,
            "general": general_vector,
            "source_card_uuids": source_card_uuids_multi_hot_vector,
            "target_card_uuids": target_card_uuids_multi_hot_vector,
            "source_card_vectors": source_card_vectors,
            "target_card_vectors": target_card_vectors,
        }

    def __card_uuids_to_multi_hot_vector(self, all_uuids, card_uuids):
        multi_hot_vector = np.zeros(len(all_uuids))
        if card_uuids is None:
            return multi_hot_vector
        for index, card_uuid in enumerate(all_uuids):
            if card_uuid in card_uuids:
                multi_hot_vector[index] = 1
        return multi_hot_vector
