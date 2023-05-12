from dataclasses import dataclass
from enum import Enum
from random import shuffle
from typing import List, Optional

from magic_the_gathering.cards.base import Card


class CardPosition(Enum):
    UNTAPPED = 0
    TAPPED = 1


@dataclass
class BoardItem:
    card: Card
    state: CardPosition


@dataclass
class StackItem:
    card: Card
    owner_player_index: int


class GameState:
    def __init__(
        self,
        hands: Optional[List[List[Card]]] = None,
        decks: Optional[List[List[Card]]] = None,
        boards: Optional[List[List[BoardItem]]] = None,
        stack: Optional[List[StackItem]] = None,
        life_totals: Optional[List[int]] = None,
    ):
        self.hands = hands
        self.decks = decks
        self.boards = boards
        self.stack = stack
        self.life_totals = life_totals

    def initialize_for_new_game(self, initial_life_points, n_players=2):
        # Set hands, decks, boards and stack to empty lists
        self.hands = [[] for _ in range(n_players)]
        self.decks = [[] for _ in range(n_players)]
        self.boards = [[] for _ in range(n_players)]
        self.stack = []

        # Set starting life points for each player
        self.life_totals = [initial_life_points for _ in range(n_players)]

    def draw_cards_from_deck(self, player_index, n_cards=1):
        n_cards = min(n_cards, len(self.decks[player_index]))
        drawn_cards = [self.decks[player_index].pop(0) for _ in range(n_cards)]
        self.hands[player_index].extend(drawn_cards)

    def add_all_hand_cards_to_deck(self, player_index):
        self.decks[player_index].extend(self.hands[player_index])
        self.hands[player_index] = []

    def shuffle_deck(self, player_index):
        shuffle(self.decks[player_index])

    def shuffle_all_decks(self):
        for player_index in range(len(self.decks)):
            self.shuffle_deck(player_index=player_index)

    def set_decks(self, decks: List[List[Card]]):
        self.decks = decks

    def cast_card(self, player_index, hand_card_index):
        card = self.hands[player_index].pop(hand_card_index)
        self.stack.append(StackItem(card=card, owner_player_index=player_index))

    def resolve_top_of_the_stack(self):
        stack_item = self.stack.pop(-1)
        board_item = BoardItem(card=stack_item.card, state=CardPosition.TAPPED)
        self.boards[stack_item.owner_player_index].append(board_item)

    def untap_all_permanents(self, player_index):
        for board_item in self.boards[player_index]:
            board_item.state = CardPosition.UNTAPPED

    def tap_cards(self, player_index, board_indices):
        for board_item in self.boards[player_index]:
            board_item.state = CardPosition.TAPPED
