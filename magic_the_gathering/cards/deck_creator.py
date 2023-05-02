import abc
import random
from typing import List

import pandas as pd

from magic_the_gathering.cards.base import Card


class DeckCreator:
    @abc.abstractmethod
    def create_decks(self, n_players=2, deck_size=60, lands_proportion=0.20) -> List[List[Card]]:
        pass


class RandomCreatureOrLandOnlyDeckCreator(DeckCreator):
    CARD_COLUMNS_TO_SELECT = [
        "uuid",
        "name",
        "rarity",
        "types",
        "subtypes",
        "colorIdentity",
        # "supertypes",
        # "colorIndicator",
        "manaCost",
        "power",
        "toughness",
        # "rulings",
        "text",
    ]

    def __init__(self, cards_csv_path):
        super().__init__()
        self.cards_csv_path = cards_csv_path
        self.cards_df = self.__load_dataframe()

    def __load_dataframe(self) -> pd.DataFrame:
        cards_df = pd.read_csv(self.cards_csv_path, usecols=RandomCreatureOrLandOnlyDeckCreator.CARD_COLUMNS_TO_SELECT)
        return self.__filter_cards(cards_df)

    def __filter_cards(self, cards_df: pd.DataFrame):
        cards_df = cards_df[cards_df["rarity"] == "common"]
        cards_df = cards_df[cards_df["types"].isin(["Creature", "Land"])]
        return cards_df.reset_index(drop=True)

    def create_decks(self, n_players=2, deck_size=60, lands_proportion=0.20) -> List[List[Card]]:
        decks = []
        for _ in range(n_players):
            deck = []
            color = random.choice(["W", "U", "B", "R", "G"])
            color_filter = self.cards_df["colorIdentity"].str.contains(color)
            land_filter = self.cards_df["types"].str.contains("Land")
            lands_deck_size = int(lands_proportion * deck_size)
            creatures_deck_size = deck_size - lands_deck_size
            print(f"Create deck of color '{color}' with {lands_deck_size} lands and {creatures_deck_size} creatures")
            creatures_deck_df = (
                self.cards_df[color_filter & ~land_filter]
                .dropna(subset=["manaCost"])
                .sample(n=creatures_deck_size, replace=True)
            )
            lands_deck_df = self.cards_df[color_filter & land_filter].sample(n=lands_deck_size, replace=True)
            deck_df = pd.concat([creatures_deck_df, lands_deck_df], axis=0)
            for _, row in deck_df.iterrows():
                card = Card.from_series(row)
                deck.append(card)
            decks.append(deck)
        return decks
