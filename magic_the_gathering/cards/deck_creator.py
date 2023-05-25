import abc
import random
from collections import OrderedDict
from typing import List, Optional

import pandas as pd

from magic_the_gathering.cards.base import Card


class DeckCreator:
    @abc.abstractmethod
    def create_decks(self, n_players: int) -> List[OrderedDict[str, Card]]:
        pass


class JumpstartDeckCreator:
    def __init__(
        self,
        card_sets_df: pd.DataFrame,
        cards_df: pd.DataFrame,
        allowed_types: Optional[List[str]] = None,
    ) -> None:
        self.card_sets_df = card_sets_df
        self.cards_df = cards_df
        self.allowed_types = allowed_types

    def create_decks(self, n_players: int) -> List[OrderedDict[str, Card]]:
        decks = []
        for _ in range(n_players):
            current_deck = OrderedDict()
            for _ in range(2):
                chosen_deck_name = random.choice(self.card_sets_df["deck_name"].unique())
                deck_composition_df = self.card_sets_df[self.card_sets_df["deck_name"] == chosen_deck_name]
                for _, row in deck_composition_df.iterrows():
                    card_name = row["card_name"]
                    card_count = row["card_count"]
                    if card_name in self.cards_df["name"].values:
                        card_series = self.cards_df[self.cards_df["name"] == card_name].iloc[0]
                        if self.allowed_types is not None:
                            card_types = card_series["type_line"].split(" — ")[0].split()
                            if not any(card_type in self.allowed_types for card_type in card_types):
                                continue
                        card = Card.from_series(card_series)
                        cards_to_add = [card] * card_count
                        for card in cards_to_add:
                            current_deck[card.uuid] = card
                    else:
                        print(f"Card '{card_name}' not found in cards dataframe")
            decks.append(current_deck)
        return decks


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
            land_color_filter = self.legal_lands_df["color_identity"] == f"['{color}']"
            land_card_names = self.legal_lands_df[land_color_filter]["name"].unique()
            creature_color_filter = self.legal_creatures_df["color_identity"] == f"['{color}']"
            creature_card_names = self.legal_creatures_df[creature_color_filter]["name"].unique()
            for _ in range(self.deck_size):
                if random.random() < self.lands_proportion:
                    card_name = random.choice(land_card_names)
                    card_series = self.legal_lands_df[self.legal_lands_df["name"] == card_name].iloc[0]
                else:
                    card_name = random.choice(creature_card_names)
                    card_series = self.legal_creatures_df[self.legal_creatures_df["name"] == card_name].iloc[0]
                card = Card.from_series(card_series)
                current_deck[card.uuid] = card
            decks.append(current_deck)
        return decks
