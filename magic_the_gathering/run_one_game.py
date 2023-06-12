import logging
import os
import random
from collections import OrderedDict
from typing import List

import pandas as pd

from magic_the_gathering.actions.draw import DrawAction
from magic_the_gathering.cards.deck_creator import RandomVanillaDeckCreator
from magic_the_gathering.game_engine import GameEngine
from magic_the_gathering.game_modes.default import DefaultGameMode
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.deep_learning_based.models.v1 import DeepLearningScorerV1
from magic_the_gathering.players.deep_learning_based.player import DeepLearningBasedPlayer


def create_decks(
    n_players: int = 2,
) -> List[List[object]]:  # FIXME: I had to remove Card because it caused a circular import
    legal_lands_df = pd.read_csv("data/basic_land_cards.csv")
    legal_creatures_df = pd.read_csv("data/vanilla_creature_cards.csv")
    deck_creator = RandomVanillaDeckCreator(
        legal_lands_df,
        legal_creatures_df,
        deck_size=60,
        lands_proportion=0.4,
    )
    decks = deck_creator.create_decks(n_players=n_players)
    for i, deck in enumerate(decks):
        items = list(deck.items())
        random.shuffle(items)
        decks[i] = OrderedDict(items)
    # TODO: Need to add Mulligan phase
    return decks


def create_hands(game_state: GameState):
    for player_index, player in enumerate(game_state.players):
        for _ in range(game_state.game_mode.initial_hand_size):
            game_state = DrawAction(player_index=player_index).execute(game_state=game_state)
    return game_state


def run_one_game(n_players: int = 2):
    log_level_env = os.getenv("LOG_LEVEL")
    log_level = logging.WARNING
    if log_level_env is not None:
        if log_level_env == "info":
            log_level = logging.INFO
        elif log_level_env == "debug":
            log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    game_mode = DefaultGameMode()
    scorer = DeepLearningScorerV1(
        n_players=n_players,
        player_dim=8,
        card_dim=34,
        action_general_dim=16,
        max_action_sequence_length=16,
        final_common_dim=32,
    )
    players = [
        DeepLearningBasedPlayer(index=index, life_points=game_mode.initial_life_points, scorer=scorer)
        for index in range(n_players)
    ]
    decks = create_decks(n_players=n_players)
    game_state = GameState(
        game_mode=game_mode,
        players=players,
    )
    game_state.set_libraries(libraries=decks)
    game_state = create_hands(game_state=game_state)
    game_engine = GameEngine(game_state=game_state)
    game_engine.run()


if __name__ == "__main__":
    run_one_game()
