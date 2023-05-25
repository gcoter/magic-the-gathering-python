import logging
from collections import OrderedDict
from time import time

import pandas as pd

from magic_the_gathering.cards.base import Card
from magic_the_gathering.cards.state import CardState
from magic_the_gathering.game_modes.default import DefaultGameMode
from magic_the_gathering.game_state import GameState, ZonePosition
from magic_the_gathering.phases.combat_beginning import CombatBeginningPhase
from magic_the_gathering.phases.combat_damage import CombatDamagePhase
from magic_the_gathering.phases.combat_declare_attackers import CombatDeclareAttackersPhase
from magic_the_gathering.phases.combat_declare_blockers import CombatDeclareBlockersPhase
from magic_the_gathering.phases.combat_end import CombatEndPhase
from magic_the_gathering.players.random import RandomPlayer


def simulate_combat():
    logging.basicConfig(level=logging.INFO)

    df = pd.read_csv("data/vanilla_creature_cards.csv")

    # Player 0 board: card scryfall IDs
    player_0_board_scryfall_ids = [
        "00223901-d462-41b0-9749-b093058f682f",  # Coral Eel
        "065d497d-5cfd-43c9-8c86-9a1da3d7e17e",  # Seagraf Skaab
        "00d89839-60d7-4de2-a78a-1afdcc21c053",  # Tolarian Scholar
        "0453fac7-10b9-49d7-8219-78faf9d92d0c",  # Fugitive Wizard
        "09ef366b-26f5-473a-ab96-e668ed54d691",  # Coral Merfolk
        "0f244233-f2e8-48f8-9106-e7cd186efd51",  # Naga Eternal
        "126fec7a-4f36-49e5-a2d7-96deb7af856f",  # Merfolk of the Pearl Trident
    ]
    player_0_board = OrderedDict()
    for scryfall_id in player_0_board_scryfall_ids:
        card = Card.from_series(df[df["id"] == scryfall_id].iloc[0])
        card.state = CardState(
            is_tapped=False,
            owner_player_id=0,
            started_turn_controlled_by_player_id=0,
        )
        player_0_board[card.uuid] = card

    # Player 1 board: card scryfall IDs
    player_1_board_scryfall_ids = [
        "0d3eff55-6a14-4c01-8b05-715094a319b3",  # Mons's Goblin Raiders
        "22955bf2-4119-40dd-a9de-25d875a93cd5",  # Hill Giant
        "11bf2cc0-799f-4eb8-b338-ed7543f469e7",  # Gray Ogre
        "13696657-aeef-4add-9a3b-8137fce01fe3",  # Crimson Kobolds
        "14a83031-8b57-41d2-b586-bb4dcf16136a",  # Trained Orgg
        "1d21c8c9-6e16-4eb2-b2f5-3998f0f958ae",  # Goblin Hero
        "1dce786c-af9c-49f5-b372-741458180a09",  # Hyena Pack
    ]
    player_1_board = OrderedDict()
    for scryfall_id in player_1_board_scryfall_ids:
        card = Card.from_series(df[df["id"] == scryfall_id].iloc[0])
        card.state = CardState(
            is_tapped=False,
            owner_player_id=1,
            started_turn_controlled_by_player_id=1,
        )
        player_1_board[card.uuid] = card

    game_state = GameState(
        game_mode=DefaultGameMode(),
        players=[RandomPlayer(), RandomPlayer()],
        current_turn_counter=5,
        current_player_index=0,
        zones={
            ZonePosition.HAND: [OrderedDict(), OrderedDict()],
            ZonePosition.LIBRARY: [OrderedDict(), OrderedDict()],
            ZonePosition.BOARD: [player_0_board, player_1_board],
            ZonePosition.GRAVEYARD: [OrderedDict(), OrderedDict()],
            ZonePosition.EXILE: [OrderedDict(), OrderedDict()],
            ZonePosition.STACK: OrderedDict(),
        },
    )

    game_state = CombatBeginningPhase().run(game_state)
    game_state = CombatDeclareAttackersPhase(force_combat=True).run(game_state)
    game_state = CombatDeclareBlockersPhase(force_combat=True).run(game_state)
    game_state = CombatDamagePhase().run(game_state)
    game_state = CombatEndPhase().run(game_state)


if __name__ == "__main__":
    elapsed_times = []
    for _ in range(100):
        start_time = time()
        simulate_combat()
        elapsed_times.append(time() - start_time)
    print(f"Average elapsed time: {sum(elapsed_times) / len(elapsed_times)} seconds")
