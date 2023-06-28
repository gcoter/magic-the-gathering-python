import logging

from magic_the_gathering.actions.base import Action
from magic_the_gathering.exceptions import GameOverException
from magic_the_gathering.game_logs_dataset import GameLogsDataset
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.mulligan import MulliganPhase
from magic_the_gathering.turn import Turn


class GameEngine:
    def __init__(self, game_state: GameState, game_logs_dataset: GameLogsDataset = None):
        self.game_state = game_state
        self.game_logs_dataset = game_logs_dataset

        self.__logger = logging.getLogger(self.__class__.__name__)
        self.mulligan_phase = MulliganPhase()
        self.turn = Turn()

    def run_one_turn(self):
        self.game_state.current_turn_counter += 1
        self.__logger.info(f"***** Turn {self.game_state.current_turn_counter} *****")
        self.__logger.debug(f"Current player is now player '{self.game_state.current_player_index}'")
        self.game_state = self.turn.run(self.game_state)

    def run(self) -> int:
        while True:
            try:
                self.run_one_turn()
            except GameOverException as e:
                winner_player_index = e.winner_player_index
                self.__logger.info(f"Player {winner_player_index} wins the game")
                if self.game_logs_dataset is not None:
                    self.game_logs_dataset.set_action_history(
                        game_id=self.game_state.game_id, action_history=Action.HISTORY
                    )
                    self.game_logs_dataset.set_winner_player_index(
                        game_id=self.game_state.game_id, winner_player_index=winner_player_index
                    )
                return winner_player_index
