from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Optional

from magic_the_gathering.actions.base import Action
from magic_the_gathering.cards.base import Card
from magic_the_gathering.exceptions import GameOverException
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
        current_player_attackers: Optional[Dict[int, List[str]]] = None,
        other_players_blockers: Optional[Dict[int, Dict[str, List[str]]]] = None,
        action_history: Optional[List[Action]] = None,
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
        self.current_player_attackers = current_player_attackers
        if self.current_player_attackers is None:
            self.current_player_attackers = {}
        self.other_players_blockers = other_players_blockers
        if self.other_players_blockers is None:
            self.other_players_blockers = {}
        self.action_history = action_history
        if self.action_history is None:
            self.action_history = []

    def __assert_zones_validity(self):
        for zone in ZonePosition:
            assert zone in self.zones
            assert len(self.zones[zone]) == self.n_players
        assert "stack" in self.zones

    def set_libraries(self, libraries: List[OrderedDict[str, Card]]):
        for player_index, library in enumerate(libraries):
            self.zones[ZonePosition.LIBRARY][player_index] = library

    @property
    def n_players(self) -> int:
        return len(self.players)

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def other_players(self) -> List[Player]:
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
