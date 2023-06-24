import json
from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

import numpy as np

from magic_the_gathering.exceptions import GameOverException
from magic_the_gathering.game_modes.base import GameMode


class ZonePosition(Enum):
    HAND = 0
    LIBRARY = 1
    BOARD = 2
    GRAVEYARD = 3
    EXILE = 4
    STACK = 5


class GameState:
    def __init__(
        self,
        game_mode: GameMode,
        players: List[object],  # FIXME: I had to remove Player because it caused a circular import
        game_id: Optional[str] = None,
        current_turn_counter: Optional[int] = 0,
        current_player_index: Optional[int] = None,
        current_player_has_played_a_land_this_turn: Optional[bool] = False,
        zones: Optional[
            Dict[ZonePosition, List[OrderedDict[str, object]]]
        ] = None,  # FIXME: I had to remove Card because it caused a circular import
        current_player_attackers: Optional[Dict[int, List[str]]] = None,
        other_players_blockers: Optional[Dict[int, Dict[str, List[str]]]] = None,
    ):
        self.game_mode = game_mode
        self.players = players
        self.game_id = game_id
        if self.game_id is None:
            self.game_id = str(uuid4())
        self.current_turn_counter = current_turn_counter
        self.current_player_index = current_player_index
        if self.current_player_index is None:
            self.current_player_index = np.random.randint(0, self.n_players)
        # TODO: Should 'current_player_has_played_a_land_this_turn' be a property of the player, not of the game state?
        # TODO: At some point we'll change this so that we allow a player to have n land drops, 1 by default, but can change with some cards
        self.current_player_has_played_a_land_this_turn = current_player_has_played_a_land_this_turn
        self.zones = zones
        if self.zones is None:
            self.zones = {
                ZonePosition.HAND: [OrderedDict() for _ in range(self.n_players)],
                ZonePosition.LIBRARY: [OrderedDict() for _ in range(self.n_players)],
                ZonePosition.BOARD: [OrderedDict() for _ in range(self.n_players)],
                ZonePosition.GRAVEYARD: [OrderedDict() for _ in range(self.n_players)],
                ZonePosition.EXILE: [OrderedDict() for _ in range(self.n_players)],
                ZonePosition.STACK: OrderedDict(),  # FIXME: It should probably be just a list but it is simpler to use the same class as the other zones for now
            }
        self.__assert_zones_validity()
        self.current_player_attackers = current_player_attackers
        if self.current_player_attackers is None:
            self.current_player_attackers = {}
        self.other_players_blockers = other_players_blockers
        if self.other_players_blockers is None:
            self.other_players_blockers = {}

    def __assert_zones_validity(self):
        for zone in ZonePosition:
            assert zone in self.zones
            if zone != ZonePosition.STACK:
                assert len(self.zones[zone]) == self.n_players
        assert ZonePosition.STACK in self.zones

    def set_libraries(
        self, libraries: List[OrderedDict[str, object]]
    ):  # FIXME: I had to remove Card because it caused a circular import
        for player_index, library in enumerate(libraries):
            self.zones[ZonePosition.LIBRARY][player_index] = library

    @property
    def n_players(self) -> int:
        return len(self.players)

    @property
    def current_player(self) -> object:  # FIXME: I had to remove Player because it caused a circular import
        return self.players[self.current_player_index]

    @property
    def other_players(self) -> List[object]:  # FIXME: I had to remove Player because it caused a circular import
        return [
            player
            for index, player in enumerate(self.players)
            if index != self.current_player_index and player.is_alive
        ]

    def check_if_game_is_over(self):
        # Conditions for game over (according to https://mtg.fandom.com/wiki/Ending_the_game):
        # - If a player concedes the game
        # - If a player’s life total is 0 or less
        # - If a player is required to draw more cards than are left in their library
        # - If a player has ten or more poison counters
        # - If an effect states that a player loses the game
        # - If an effect states that the game is a draw
        # - If a player would both win and lose the game simultaneously

        # For now, we only check if all players except one are dead
        alive_player_indices = [player_index for player_index, player in enumerate(self.players) if player.is_alive]
        if len(alive_player_indices) == 1:
            winner_player_index = alive_player_indices[0]
            raise GameOverException(winner_player_index=winner_player_index)

    def to_json_dict(self) -> Dict:
        json_dict = {
            "game_id": self.game_id,
            "game_mode": self.game_mode.to_json_dict(),
            "players": [player.to_json_dict() for player in self.players],
            "current_turn_counter": self.current_turn_counter,
            "current_player_index": self.current_player_index,
            "current_player_has_played_a_land_this_turn": self.current_player_has_played_a_land_this_turn,
            "zones": {
                zone.name: [
                    card.to_json_dict()
                    for player_index in range(self.n_players)
                    for card in self.zones[zone][player_index].values()
                ]
                for zone in self.zones.keys()
                if zone != ZonePosition.STACK and zone != ZonePosition.LIBRARY
            },
            "current_player_attackers": self.current_player_attackers,
            "other_players_blockers": self.other_players_blockers,
        }
        json_dict["zones"][ZonePosition.STACK.name] = [
            card.to_json_dict() for card in self.zones[ZonePosition.STACK].values()
        ]
        return json_dict

    def save_as_json(self, file_path: str):
        json_dict = self.to_json_dict()
        with open(file_path, "w") as f:
            json.dump(json_dict, f, indent=4)

    def to_vectors(self) -> Dict[str, np.ndarray]:
        return {
            "global": self.global_to_vector(),
            "players": self.players_to_vector(),
            "zones": self.zones_to_vector(),
        }

    def players_to_vector(self) -> np.ndarray:
        players_vectors = []
        for player_index, player in enumerate(self.players):
            player_vector = player.to_vector()
            is_current_player_vector = np.array([1 if player_index == self.current_player_index else 0])
            vector = np.concatenate([player_vector, is_current_player_vector])
            players_vectors.append(vector)
        return np.array(players_vectors).astype(np.float32)

    def global_to_vector(self) -> np.ndarray:
        return np.array([self.current_turn_counter, self.current_player_has_played_a_land_this_turn]).astype(np.float32)

    def zones_to_vector(self, return_uuids=False) -> np.ndarray:
        zones_vectors = []
        uuids = []
        for zone in ZonePosition:
            if zone == ZonePosition.STACK:
                for card_uuid, card in self.zones[zone].items():
                    card_vector = card.to_vector()
                    card_owner_one_hot_vector = self.player_index_to_one_hot_vector(card.state.owner_player_id)
                    started_turn_controlled_by_player_one_hot_vector = self.player_index_to_one_hot_vector(
                        card.state.started_turn_controlled_by_player_id
                    )
                    player_index_vector = np.zeros(self.n_players)
                    zone_vector = self.zone_position_to_one_hot_vector(zone)
                    uuids.append(card_uuid)
                    vector = np.concatenate(
                        [
                            card_vector,
                            card_owner_one_hot_vector,
                            started_turn_controlled_by_player_one_hot_vector,
                            player_index_vector,
                            zone_vector,
                        ]
                    )
                    zones_vectors.append(vector)
            elif zone != ZonePosition.LIBRARY:
                for player_index in range(self.n_players):
                    for card_uuid, card in self.zones[zone][player_index].items():
                        card_vector = card.to_vector()
                        card_owner_one_hot_vector = self.player_index_to_one_hot_vector(
                            card.state.owner_player_id if card.state is not None else None
                        )
                        started_turn_controlled_by_player_one_hot_vector = self.player_index_to_one_hot_vector(
                            card.state.started_turn_controlled_by_player_id if card.state is not None else None
                        )
                        player_index_vector = self.player_index_to_one_hot_vector(player_index)
                        zone_vector = self.zone_position_to_one_hot_vector(zone)
                        uuids.append(card_uuid)
                        vector = np.concatenate(
                            [
                                card_vector,
                                card_owner_one_hot_vector,
                                started_turn_controlled_by_player_one_hot_vector,
                                player_index_vector,
                                zone_vector,
                            ]
                        )
                        zones_vectors.append(vector)
        final_array = np.array(zones_vectors).astype(np.float32)
        if return_uuids:
            return final_array, uuids
        return final_array

    def player_index_to_one_hot_vector(self, player_index: int = None) -> np.ndarray:
        one_hot_vector = np.zeros(self.n_players)
        if player_index is not None:
            one_hot_vector[player_index] = 1
        return one_hot_vector

    def zone_position_to_one_hot_vector(self, zone: ZonePosition = None) -> np.ndarray:
        one_hot_vector = np.zeros(len(ZonePosition))
        if zone is not None:
            one_hot_vector[zone.value] = 1
        return one_hot_vector
