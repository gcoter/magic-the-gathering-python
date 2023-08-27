import abc
import random
from collections import OrderedDict
from typing import List

import pandas as pd

from magic_the_gathering.cards.base import Card


class DeckCreator:
    @abc.abstractmethod
    def create_decks(self, n_players: int) -> List[OrderedDict[str, Card]]:
        pass


class RandomVanillaDeckCreator:
    def __init__(
        self,
        legal_lands_df: pd.DataFrame,
        legal_creatures_df: pd.DataFrame,
        deck_size: int = 60,
        lands_proportion: float = 0.4,
    ) -> None:
        self.legal_lands_df = legal_lands_df
        self.legal_creatures_df = legal_creatures_df
        self.deck_size = deck_size
        self.lands_proportion = lands_proportion

    def create_decks(self, n_players: int) -> List[OrderedDict[str, Card]]:
        decks = []
        for _ in range(n_players):
            current_deck = OrderedDict()
            color = random.choice(["W", "U", "B", "R", "G"])
            for _ in range(self.deck_size):
                self.add_a_card_at_random(color, current_deck)
            decks.append(current_deck)
        return decks

    def add_a_card_at_random(
        self,
        color: str,
        current_deck: OrderedDict[str, Card],
    ) -> OrderedDict[str, Card]:
        creature_color_filter = self.legal_creatures_df["color_identity"] == f"['{color}']"
        creature_card_names = self.legal_creatures_df[creature_color_filter]["name"].unique()
        land_color_filter = self.legal_lands_df["color_identity"] == f"['{color}']"
        land_card_names = self.legal_lands_df[land_color_filter]["name"].unique()

        if random.random() < self.lands_proportion:
            card_name = random.choice(land_card_names)
            card_series = self.legal_lands_df[self.legal_lands_df["name"] == card_name].iloc[0]
        else:
            card_name = random.choice(creature_card_names)
            card_series = self.legal_creatures_df[self.legal_creatures_df["name"] == card_name].iloc[0]

        card = Card.from_series(card_series)
        print(f"Adding {card.name} to the deck")
        current_deck[card.uuid] = card
        return current_deck
