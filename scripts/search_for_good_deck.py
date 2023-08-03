import copy
import logging
import math
import os
import random
import time
from functools import lru_cache
from typing import List, OrderedDict

import pandas as pd

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.draw import DrawAction
from magic_the_gathering.cards.deck_creator import RandomVanillaDeckCreator
from magic_the_gathering.game_engine import GameEngine
from magic_the_gathering.game_logs_dataset import GameLogsDataset
from magic_the_gathering.game_modes.base import GameMode
from magic_the_gathering.game_modes.default import DefaultGameMode
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.random import RandomPlayer


def print_execution_time(func):
    """
    Decorator that, when applied to a function/method, adds the functionality of printing the execution time
    :param func: function to apply this decorator to
    :return: what the func returns
    """

    def wrapper(*arg, **kw):
        start_time = time.time()
        result = func(*arg, **kw)
        time_delta = time.time() - start_time
        print(f"Function '{func.__name__}' executed in {round(time_delta, 1)} seconds")
        return result

    return wrapper


@print_execution_time
def search_for_arena_winner(
    consecutive_test_wins_threshold: int = 2,
    games_limit_per_test: int = 100,
    p_value: float = 0.05,
) -> OrderedDict[str, object]:
    """
    Looks for an arena champion deck until one is found.
    A champion deck is a deck that is tested as significantly better than a random deck consecutive_test_wins_threshold
     times in a row.
    To identify whether a deck is significantly better than another, we run up to games_limit_per_test games between the
     two decks and stop as soon as the probability for the record obtained to happen under the assumption of 50% winrate
     is lower than p_value.
    :return: The champion deck
    """
    decks = create_decks(n_players=2)
    return search_for_arena_winner_recursive(
        decks=decks,
        consecutive_test_wins=0,
        consecutive_test_wins_threshold=consecutive_test_wins_threshold,
        games_limit=games_limit_per_test,
        p_value=p_value,
    )


def search_for_arena_winner_recursive(
    decks: list[OrderedDict[str, object]],
    consecutive_test_wins: int = 0,
    consecutive_test_wins_threshold: int = 2,
    games_limit: int = 100,
    p_value: float = 0.05,
) -> OrderedDict[str, object]:
    print(f"\nConsecutive test wins of deck in the arena is {consecutive_test_wins}")

    if consecutive_test_wins >= consecutive_test_wins_threshold:
        return decks[0]

    winner_player_index = get_index_of_best_deck(decks=copy.deepcopy(decks), games_limit=games_limit, p_value=p_value)

    new_opponent_deck = create_decks(n_players=1)[0]
    if winner_player_index is None:
        print("No clear better deck has been identified, going to the next opponent")
        return search_for_arena_winner_recursive(
            decks=[copy.deepcopy(decks)[0], new_opponent_deck],
            consecutive_test_wins=consecutive_test_wins,
            consecutive_test_wins_threshold=consecutive_test_wins_threshold,
            games_limit=games_limit,
            p_value=p_value,
        )

    if winner_player_index == 1:
        print(f"Champion has been beaten after {consecutive_test_wins} consecutive wins by")
        print(get_deck_simple_repr(decks[1]))

    return search_for_arena_winner_recursive(
        decks=[copy.deepcopy(decks)[winner_player_index], new_opponent_deck],
        consecutive_test_wins=consecutive_test_wins + 1 if winner_player_index == 0 else 0,
        consecutive_test_wins_threshold=consecutive_test_wins_threshold,
        games_limit=games_limit,
        p_value=p_value,
    )


def get_index_of_best_deck(
    decks: list[OrderedDict[str, object]], games_limit: int = 100, p_value: float = 0.05
) -> int | None:
    games_count = 0
    wins_count = 0
    while games_count < games_limit:
        winner_player_index = simulate_one_game(decks=decks)
        games_count += 1
        if winner_player_index == 0:
            wins_count += 1
        wins_of_player_with_most_wins = max(wins_count, games_count - wins_count)
        p_decks_are_equivalently_powerful = get_probability_of_at_least_k_heads_in_n_flips(
            wins_of_player_with_most_wins, games_count
        )
        # print(
        #    f"Probability that decks are equivalently powerful with {wins_of_player_with_most_wins} wins out of {games_count}: {p_decks_are_equivalently_powerful}"
        # )
        if p_decks_are_equivalently_powerful <= p_value:
            print(f"After {games_count} games, a deck has been identified as being significantly better")
            return 0 if wins_count / games_count >= 0.5 else 1


def simulate_one_game(decks: list[OrderedDict[str, object]]) -> int:
    game_mode = DefaultGameMode()
    Action.HISTORY = []
    players = create_players(2, game_mode)
    game_state = GameState(
        game_mode=game_mode,
        players=players,
    )
    game_state.set_libraries(libraries=copy.deepcopy(decks))
    game_state = create_hands(game_state=game_state)
    game_engine = GameEngine(game_state=game_state)
    return game_engine.run()


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
) -> List[OrderedDict[str, object]]:  # FIXME: I had to remove Card because it caused a circular import
    legal_lands_df = pd.read_csv("data/basic_land_cards.csv")
    legal_creatures_df = pd.read_csv("data/vanilla_creature_cards.csv")
    deck_creator = RandomVanillaDeckCreator(
        legal_lands_df,
        legal_creatures_df,
        deck_size=40,
        lands_proportion=17 / 40,
    )
    decks = deck_creator.create_decks(n_players=n_players)
    for i, deck in enumerate(decks):
        items = list(deck.items())
        random.shuffle(items)
        decks[i] = OrderedDict(items)
    return decks


def create_hands(game_state: GameState):
    for player_index, player in enumerate(game_state.players):
        for _ in range(game_state.game_mode.initial_hand_size):
            game_state = DrawAction(player_index=player_index).execute(game_state=game_state)
    return game_state


def create_players(
    n: int,
    game_mode: GameMode,
    game_logs_dataset: GameLogsDataset = None,
):
    return [
        RandomPlayer(
            index=index,
            life_points=game_mode.initial_life_points,
            game_logs_dataset=game_logs_dataset,
        )
        for index in range(n)
    ]


@lru_cache(maxsize=None)
def get_probability_of_at_least_k_heads_in_n_flips(k: int, n: int) -> float:
    return sum(get_probability_of_k_heads_in_n_flips(i, n) for i in range(k, n + 1))


@lru_cache(maxsize=None)
def get_probability_of_k_heads_in_n_flips(k: int, n: int) -> float:
    return get_k_in_n(k, n) / 2**n


@lru_cache(maxsize=None)
def get_k_in_n(k: int, n: int) -> float:
    return math.comb(n, k)


def get_deck_simple_repr(deck: OrderedDict[str, object]) -> str:
    cards = list(deck.values())
    sorted_cards = sorted(cards, key=lambda c: (c.mana_value, c.name))

    lands = [card for card in sorted_cards if card.is_land]
    nonlands = [card for card in sorted_cards if not card.is_land]

    nonland_str = "\n".join([str(card) for card in nonlands])

    return f"{nonland_str}\n{str(pd.Series([card.name for card in lands]).value_counts())[:-26]}"


if __name__ == "__main__":
    champion_deck = search_for_arena_winner(
        consecutive_test_wins_threshold=10,
        games_limit_per_test=50,
        p_value=0.05,
    )
    simple_print_deck(champion_deck)
