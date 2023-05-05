import abc
import random
from typing import List, Optional

import pandas as pd

from magic_the_gathering.cards.base import Card


class DeckCreator:
    @abc.abstractmethod
    def create_decks(self, n_players: int) -> List[List[Card]]:
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

    def create_decks(self, n_players: int) -> List[List[Card]]:
        decks = []
        for _ in range(n_players):
            current_deck = []
            for _ in range(2):
                chosen_deck_name = random.choice(self.card_sets_df["deck_name"].unique())
                deck_composition_df = self.card_sets_df[self.card_sets_df["deck_name"] == chosen_deck_name]
                for _, row in deck_composition_df.iterrows():
                    card_name = row["card_name"]
                    n_occurences = row["n_occurences"]
                    card_series = self.cards_df[self.cards_df["name"] == card_name].iloc[0]
                    if self.allowed_types is not None:
                        card_types = card_series["type_line"].split(" — ")[0].split()
                        if not any(card_type in self.allowed_types for card_type in card_types):
                            continue
                    card = Card.from_series(card_series)
                    current_deck.extend([card] * n_occurences)
            decks.append(current_deck)
        return decks
