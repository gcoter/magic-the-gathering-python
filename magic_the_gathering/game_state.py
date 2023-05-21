from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Optional

from magic_the_gathering.cards.base import Card
from magic_the_gathering.game_modes.base import GameMode
from magic_the_gathering.players.base import Player


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
        players: List[Player],
        current_turn_counter: Optional[int] = 0,
        current_player_index: Optional[int] = 0,
        current_player_has_played_a_land_this_turn: Optional[bool] = False,
        zones: Optional[Dict[ZonePosition, List[OrderedDict[str, Card]]]] = None,
    ):
        self.game_mode = game_mode
        self.players = players
        self.current_turn_counter = current_turn_counter
        self.current_player_index = current_player_index
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

    def __assert_zones_validity(self):
        for zone in ZonePosition:
            assert zone in self.zones
            assert len(self.zones[zone]) == self.n_players
        assert "stack" in self.zones

    @property
    def n_players(self):
        return len(self.players)

    @property
    def current_player(self):
        return self.players[self.current_player_index]
