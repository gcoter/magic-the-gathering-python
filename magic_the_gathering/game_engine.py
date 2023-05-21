import logging

from magic_the_gathering.cards.deck_creator import DeckCreator
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.mulligan import MulliganPhase
from magic_the_gathering.turn import Turn


class GameEngine:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.__logger = logging.getLogger(self.__class__.__name__)
        self.mulligan_phase = MulliganPhase()
        self.turn = Turn()

    def start_new_game(self, deck_creator: DeckCreator):
        # TODO: Should we put all of this inside a 'NewGamePhase'?

        self.__logger.info("Starting a new game")

        # Initialize the game state
        self.game_state.initialize_for_new_game(
            initial_life_points=GameEngine.INITIAL_LIFE_TOTAL, n_players=len(self.players)
        )

        # Create a shuffled deck for each player
        # TODO: should we split the deck creation and start_new_game, so that we can can start several games with the same deck(s)?
        decks = deck_creator.create_decks(n_players=len(self.players))
        self.game_state.set_decks(decks)
        self.game_state.shuffle_all_decks()

        # Players draw cards to start the game
        self.game_state = self.mulligan_phase.run(self.game_state)

    def run_one_turn(self):
        self.game_state.current_turn_counter += 1
        self.__logger.info(f"Start turn {self.game_state.current_turn_counter}")
        self.__logger.debug(f"Current player is now player '{self.game_state.current_player_index}'")
        self.game_state = self.turn.run(self.game_state)
