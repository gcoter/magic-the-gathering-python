import logging
from typing import List

import numpy as np

from magic_the_gathering.cards.deck_creator import DeckCreator
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.base import Player


class GameEngine:
    N_STARTING_CARDS = 7
    INITIAL_LIFE_POINTS = 20
    DECK_SIZE = 60
    LANDS_PROPORTION = 0.20

    def __init__(self, game_state: GameState, players: List[Player]):
        self.game_state = game_state
        self.players = players

        self.__current_turn_counter = 0
        self.__current_player_index = 0
        self.__current_player_has_cast_a_land_this_turn = False

        self.__logger = logging.getLogger(self.__class__.__name__)

    def start_new_game(self, deck_creator: DeckCreator):
        self.__logger.info("Starting a new game")

        # Initialize the game state
        self.game_state.initialize_for_new_game(
            initial_life_points=GameEngine.INITIAL_LIFE_POINTS, n_players=len(self.players)
        )

        # Create a shuffled deck for each player
        decks = deck_creator.create_decks(
            n_players=len(self.players), deck_size=GameEngine.DECK_SIZE, lands_proportion=GameEngine.LANDS_PROPORTION
        )
        self.game_state.set_decks(decks)
        self.game_state.shuffle_all_decks()

        # Players draw cards to start the game
        self.__players_draw_cards_and_take_mulligans()

    def __players_draw_cards_and_take_mulligans(self):
        take_mulligan_by_player = np.array([False for _ in range(self.players)])
        n_cards_to_draw_by_player = np.array([GameEngine.N_STARTING_CARDS for _ in range(self.players)])
        while True:
            for index, player in enumerate(self.players):
                # Each player draws as many cards as necessary to create their hand
                if len(self.game_state.hands[index]) == 0:
                    self.game_state.draw_cards_from_deck(player_index=index, n_cards=n_cards_to_draw_by_player[index])

                if take_mulligan_by_player[index]:
                    self.__logger.info(f"Player '{index}' takes a mulligan")
                    self.game_state.add_all_hand_cards_to_deck(player_index=index)
                    self.game_state.shuffle_deck(player_index=index)
                    self.game_state.draw_cards_from_deck(player_index=index, n_cards=n_cards_to_draw_by_player[index])

                # Each player decides whether they want to take a mulligan
                take_mulligan_by_player[index] = player.choose_mulligan(game_state=self.game_state)
                if take_mulligan_by_player[index]:
                    n_cards_to_draw_by_player[index] -= 1

                # If a mulligan would cause a player to draw no card, then forbid it
                if n_cards_to_draw_by_player[index] <= 0:
                    take_mulligan_by_player[index] = False

            if ~np.any(take_mulligan_by_player):
                break

    def run_one_turn(self):
        self.__current_turn_counter += 1
        self.__logger.info(f"Start turn {self.__current_turn_counter}")
        self.__logger.debug(f"Current player is now player '{self.__current_player_index}'")

        self.__begin_phase()

        if not self.__is_the_game_over():
            self.__precombat_main_phase()

        if not self.__is_the_game_over():
            self.__combat_phase()

        if not self.__is_the_game_over():
            self.__postcombat_main_phase()

        self.__end_phase()

    def __is_the_game_over(self) -> bool:
        # If a player’s life total is 0 or less
        # If a player is required to draw more cards than are left in their library
        # If a player has ten or more poison counters
        # If an effect states that a player loses the game
        # If an effect states that the game is a draw
        # If a player would both win and lose the game simultaneously
        pass

    def __begin_phase(self):
        self.__logger.debug("Run begin phase")
        self.__current_player_has_cast_a_land_this_turn = False

        # Current player untaps lands and creatures
        self.game_state.untap_all_cards(player_index=self.__current_player_index)

        # Current player draws one card
        self.game_state.draw_cards_from_deck(player_index=self.__current_player_index, n_cards=1)

    def __precombat_main_phase(self):
        self.__logger.debug("Run precombat main phase")

        # Current player can cast a land (only 1 per turn)
        self.__current_player_has_cast_a_land_this_turn = self.__current_player_can_cast_one_land()

        # Current player can cast creatures and/or sorceries
        self.__current_player_can_cast_creatures_and_sorceries()

    def __combat_phase(self):
        self.__logger.debug("Run combat phase")

        # Current player can declare attackers
        attackers_board_indices, target_player_indices = self.current_player.choose_attackers()
        self.game_state.tap_cards(player_index=self.__current_player_index, board_indices=attackers_board_indices)

        # Opponent declares blockers
        for targetted_player_index in set(target_player_indices):
            blockers_board_indices, target_attacker_indices = self.players[targetted_player_index].choose_blockers()

            # Combat damage is dealt
            pass

    def __postcombat_main_phase(self):
        self.__logger.debug("Run postcombat main phase")

        # Current player can play a land (if he has not already)
        if not self.__current_player_has_cast_a_land_this_turn:
            self.__current_player_can_cast_one_land()

        # Current player can cast creatures and/or sorceries
        self.__current_player_can_cast_creatures_and_sorceries()

    def __end_phase(self):
        self.__logger.debug("Run end phase")

        # Current player's creatures heal
        pass

        # Pass the turn to the next player
        self.__pass_to_next_player()

    def __current_player_can_cast_one_land(self) -> bool:
        hand_card_index = self.current_player.choose_land_to_cast()
        if hand_card_index is not None:
            self.game_state.cast_card(player_index=self.__current_player_index, hand_card_index=hand_card_index)
            self.game_state.resolve_top_of_the_stack()
        return hand_card_index is not None

    def __current_player_can_cast_creatures_and_sorceries(self):
        hand_card_indices = self.current_player.choose_creatures_to_cast()
        for hand_card_index in hand_card_indices:
            self.game_state.cast_card(player_index=self.__current_player_index, hand_card_index=hand_card_index)
            self.game_state.resolve_top_of_the_stack()

    @property
    def current_player(self) -> Player:
        return self.players[self.__current_player_index]

    @property
    def other_players(self) -> List[Player]:
        return [player for index, player in enumerate(self.players) if index != self.__current_player_index]

    def __pass_to_next_player(self):
        self.__logger.debug("Pass to next player")
        self.__current_player_index = (self.__current_player_index + 1) % len(self.players)
