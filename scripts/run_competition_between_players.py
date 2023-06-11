import logging
import os
import random
from typing import List, OrderedDict

import pandas as pd
from fire import Fire

from magic_the_gathering.actions.draw import DrawAction
from magic_the_gathering.cards.deck_creator import RandomVanillaDeckCreator
from magic_the_gathering.game_engine import GameEngine
from magic_the_gathering.game_modes.base import GameMode
from magic_the_gathering.game_modes.default import DefaultGameMode
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.deep_learning_based.models.v1 import DeepLearningScorerV1
from magic_the_gathering.players.deep_learning_based.player import DeepLearningBasedPlayer
from magic_the_gathering.players.random import RandomPlayer


def set_logging_level():
    log_level_env = os.getenv("LOG_LEVEL")
    log_level = logging.WARNING
    if log_level_env is not None:
        if log_level_env == "info":
            log_level = logging.INFO
        elif log_level_env == "debug":
            log_level = logging.DEBUG

    logging.basicConfig(level=log_level)


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


def create_players(game_mode: GameMode, players_classes: List[str]):
    n_players = len(players_classes)
    string_to_player = {"random": RandomPlayer, "deep_learning": DeepLearningBasedPlayer}
    players = []
    for index, player_class in enumerate(players_classes):
        if player_class == "deep_learning":
            scorer = DeepLearningScorerV1(
                n_players=n_players,
                player_dim=8,
                card_dim=34,
                action_general_dim=16,
                max_action_sequence_length=16,
                final_common_dim=32,
            )
            player = string_to_player[player_class](
                index=index, life_points=game_mode.initial_life_points, scorer=scorer
            )
        else:
            player = string_to_player[player_class](index=index, life_points=game_mode.initial_life_points)
        players.append(player)
    return players


def run_competition_between_players(n_games: int, player_classes: List[str], log_directory_path: str = None):
    set_logging_level()

    n_players = len(player_classes)
    game_mode = DefaultGameMode()
    win_counts = {i: 0 for i in range(n_players)}

    print(f"\n===== Start competition between players: {player_classes} =====\n")

    for n in range(n_games):
        print(f"\n***** Game {n + 1} / {n_games} *****")
        players = create_players(game_mode=game_mode, players_classes=player_classes)
        decks = create_decks(n_players=n_players)
        game_state = GameState(
            game_mode=game_mode,
            players=players,
        )
        game_state.set_libraries(libraries=decks)
        game_state = create_hands(game_state=game_state)
        game_engine = GameEngine(game_state=game_state, log_directory_path=log_directory_path)
        winner_player_index = game_engine.run()
        win_counts[winner_player_index] += 1

    print("\n===== Win Rates =====")
    for player_index, win_count in win_counts.items():
        win_rate = win_count / n_games
        print(f"- Player '{player_classes[player_index]}': {win_rate * 100:.2f}%")


if __name__ == "__main__":
    Fire(run_competition_between_players)
