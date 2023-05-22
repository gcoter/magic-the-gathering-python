import logging
import random
from collections import OrderedDict
from typing import List

import pandas as pd

from magic_the_gathering.actions.draw import DrawAction
from magic_the_gathering.cards.deck_creator import JumpstartDeckCreator
from magic_the_gathering.game_engine import GameEngine
from magic_the_gathering.game_modes.default import DefaultGameMode
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.random import RandomPlayer


def create_decks(
    n_players: int = 2,
) -> List[List[object]]:  # FIXME: I had to remove Card because it caused a circular import
    jmp_decklist_df = pd.read_csv("data/jmp_decklist.csv")
    j22_decklist_df = pd.read_csv("data/j22_decklist.csv")
    cards_df = pd.read_csv("data/jumpstart_cards.csv")
    jmp_and_j22_decklist_df = pd.concat([jmp_decklist_df, j22_decklist_df]).reset_index(drop=True)
    deck_creator = JumpstartDeckCreator(
        card_sets_df=jmp_and_j22_decklist_df, cards_df=cards_df, allowed_types=["Creature", "Land"]
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
            game_state = DrawAction(owner="game", player_index=player_index).execute(game_state=game_state)
    return game_state


def run_one_game(n_players: int = 2):
    logging.basicConfig(level=logging.DEBUG)

    game_mode = DefaultGameMode()
    players = [RandomPlayer(life_points=game_mode.initial_life_points)] * n_players
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
