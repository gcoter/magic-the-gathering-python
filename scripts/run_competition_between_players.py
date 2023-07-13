import json
import logging
import os
import pickle
import random
from pathlib import Path
from typing import Dict, List, OrderedDict

import pandas as pd
import torch
import yaml
from fire import Fire

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.draw import DrawAction
from magic_the_gathering.cards.deck_creator import RandomVanillaDeckCreator
from magic_the_gathering.game_engine import GameEngine
from magic_the_gathering.game_logs_dataset import GameLogsDataset
from magic_the_gathering.game_modes.base import GameMode
from magic_the_gathering.game_modes.default import DefaultGameMode
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.deep_learning_based.player import DeepLearningBasedPlayer
from magic_the_gathering.players.deep_learning_based.single_action_scorer.models.v2 import SingleActionScorerV2
from magic_the_gathering.players.random import RandomPlayer
from magic_the_gathering.utils import set_random_seed


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


def create_players(
    game_mode: GameMode,
    players_classes: List[str],
    game_logs_dataset: GameLogsDataset = None,
    deep_learning_scorer_path: str = None,
    hyper_parameters: Dict = None,
):
    n_players = len(players_classes)
    string_to_player = {"random": RandomPlayer, "deep_learning": DeepLearningBasedPlayer}
    players = []
    for index, player_class in enumerate(players_classes):
        if player_class == "deep_learning":
            assert hyper_parameters is not None
            scorer = SingleActionScorerV2(**hyper_parameters)
            if deep_learning_scorer_path is not None:
                checkpoint = torch.load(deep_learning_scorer_path)
                scorer.load_state_dict(checkpoint["state_dict"])
            player = string_to_player[player_class](
                index=index,
                life_points=game_mode.initial_life_points,
                scorer=scorer,
                game_logs_dataset=game_logs_dataset,
            )
        else:
            player = string_to_player[player_class](
                index=index, life_points=game_mode.initial_life_points, game_logs_dataset=game_logs_dataset
            )
        players.append(player)
    return players


def read_params(path: str) -> Dict:
    with open(path, "r") as f:
        params = yaml.safe_load(f)
    return params


def run_competition_between_players(
    n_games: int,
    player_classes: List[str],
    params_path: str,
    evaluation_metrics_json_path: str = None,
    game_logs_stats_json_path: str = None,
    game_logs_dataset_path: str = None,
    deep_learning_scorer_path: str = None,
):
    set_random_seed(seed=42)
    set_logging_level()

    print(f"Load parameters from '{params_path}'")
    params = read_params(params_path)["deep_learning_scorer"]

    n_players = len(player_classes)
    game_mode = DefaultGameMode()
    win_counts = {i: 0 for i in range(n_players)}

    game_logs_dataset = GameLogsDataset()

    print(f"\n===== Start competition between players: {player_classes} =====\n")

    for n in range(n_games):
        print(f"\n***** Game {n + 1} / {n_games} *****")
        Action.HISTORY = []
        players = create_players(
            game_mode=game_mode,
            players_classes=player_classes,
            game_logs_dataset=game_logs_dataset,
            deep_learning_scorer_path=deep_learning_scorer_path,
            hyper_parameters=params["hyper_parameters"],
        )
        decks = create_decks(n_players=n_players)
        game_state = GameState(
            game_mode=game_mode,
            players=players,
        )
        game_state.set_libraries(libraries=decks)
        game_state = create_hands(game_state=game_state)
        game_engine = GameEngine(game_state=game_state, game_logs_dataset=game_logs_dataset)
        winner_player_index = game_engine.run()
        win_counts[winner_player_index] += 1

    print("\n===== Win Rates =====")
    for player_index, win_count in win_counts.items():
        win_rate = win_count / n_games
        print(f"- Player '{player_classes[player_index]}': {win_rate * 100:.2f}%")

    if evaluation_metrics_json_path is not None:
        Path(evaluation_metrics_json_path).parent.mkdir(parents=True, exist_ok=True)
        print("\n===== Save evaluation metrics =====")
        metrics_dict = {
            "n_games": n_games,
            "win_counts": {
                f"player_{index}": win_count
                for index, (player_class, win_count) in enumerate(zip(player_classes, win_counts.values()))
            },
            "win_rates": {
                f"player_{index}": win_count / n_games
                for index, (player_class, win_count) in enumerate(zip(player_classes, win_counts.values()))
            },
        }
        with open(evaluation_metrics_json_path, "w") as f:
            json.dump(metrics_dict, f, indent=4)

    if game_logs_stats_json_path is not None:
        Path(game_logs_stats_json_path).parent.mkdir(parents=True, exist_ok=True)
        print("\n===== Save game logs stats =====")
        metrics_dict = game_logs_dataset.compute_stats()
        with open(game_logs_stats_json_path, "w") as f:
            json.dump(metrics_dict, f, indent=4)

    if game_logs_dataset_path is not None:
        assert game_logs_dataset is not None
        print(f"Save game logs dataset to '{game_logs_dataset_path}'")
        with open(game_logs_dataset_path, "wb") as f:
            pickle.dump(game_logs_dataset, f)


if __name__ == "__main__":
    Fire(run_competition_between_players)
