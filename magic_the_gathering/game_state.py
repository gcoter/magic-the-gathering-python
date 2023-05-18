from random import shuffle
from typing import List, Optional

from magic_the_gathering.cards.base import Card
from magic_the_gathering.game_modes.base import GameMode
from magic_the_gathering.players.base import Player


class GameState:
    def __init__(
        self,
        game_mode: GameMode,
        players: List[Player],
        current_turn_counter: Optional[int] = 0,
        current_player_index: Optional[int] = 0,
        current_player_has_played_a_land_this_turn: Optional[bool] = False,
        hands: Optional[List[List[Card]]] = None,
        libraries: Optional[List[List[Card]]] = None,
        boards: Optional[List[List[Card]]] = None,
        graveyards: Optional[List[List[Card]]] = None,
        exiles: Optional[List[Card]] = None,
        stack: Optional[List[Card]] = None,
    ):
        self.game_mode = game_mode
        self.players = players
        self.current_turn_counter = current_turn_counter
        self.current_player_index = current_player_index
        # TODO: Should 'current_player_has_played_a_land_this_turn' be a property of the player, not of the game state?
        # TODO: At some point we'll change this so that we allow a player to have n land drops, 1 by default, but can change with some cards
        self.current_player_has_played_a_land_this_turn = current_player_has_played_a_land_this_turn
        self.hands = hands
        self.libraries = libraries
        self.boards = boards
        self.graveyards = graveyards
        self.exiles = exiles
        self.stack = stack

    @property
    def n_players(self):
        return len(self.players)

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def initialize_for_new_game(self):
        # TODO: It assumes that the players were initialized, is it a good idea?
        # FIXME: The game mode contains information about the player initial life points and hand size, but it is not used here
        # TODO: Pass the current player index? (for now it is always 0)
        # Set hands, libraries, boards and stack to empty lists
        self.hands = [[] for _ in range(self.n_players)]
        self.libraries = [[] for _ in range(self.n_players)]
        self.boards = [[] for _ in range(self.n_players)]
        self.graveyards = [[] for _ in range(self.n_players)]
        # TODO: Is there one exile per player?
        self.exiles = [[] for _ in range(self.n_players)]
        self.stack = []

    def draw_cards_from_deck(self, player_index, n_cards=1):
        n_cards = min(n_cards, len(self.libraries[player_index]))
        drawn_cards = [self.libraries[player_index].pop(0) for _ in range(n_cards)]
        self.hands[player_index].extend(drawn_cards)

    def add_all_hand_cards_to_deck(self, player_index):
        self.libraries[player_index].extend(self.hands[player_index])
        self.hands[player_index] = []

    def shuffle_deck(self, player_index):
        shuffle(self.libraries[player_index])

    def shuffle_all_decks(self):
        for player_index in range(len(self.libraries)):
            self.shuffle_deck(player_index=player_index)

    def set_decks(self, decks: List[List[Card]]):
        self.libraries = decks

    def play_card(self, player_index, hand_card_index):
        card = self.hands[player_index].pop(hand_card_index)
        card.is_tapped = False
        self.boards[card.owner_player_index].append(card)

    def cast_card(self, player_index, hand_card_index):
        card = self.hands[player_index].pop(hand_card_index)
        self.stack.append(card)

    def resolve_top_of_the_stack(self):
        # TODO: Currently, this was implemented with casting creatures or lands in mind. It should be generalized.
        card = self.stack.pop(-1)
        card.is_tapped = False
        self.boards[card.owner_player_index].append(card)

    def untap_all_permanents(self, player_index: int):
        for permanent in self.boards[player_index]:
            permanent.is_tapped = False

    def tap_cards(self, player_index, board_indices):
        for board_index in board_indices:
            self.boards[player_index][board_index].is_tapped = True

    def pass_to_next_player(self):
        self.current_player_index = (self.current_player_index + 1) % self.n_players
