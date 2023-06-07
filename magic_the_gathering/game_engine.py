import json
import logging
import os

from magic_the_gathering.exceptions import GameOverException
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.mulligan import MulliganPhase
from magic_the_gathering.turn import Turn


class GameEngine:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

        self.__logger = logging.getLogger(self.__class__.__name__)
        self.mulligan_phase = MulliganPhase()
        self.turn = Turn()

    def run_one_turn(self):
        self.game_state.current_turn_counter += 1
        self.__logger.info(f"***** Turn {self.game_state.current_turn_counter} *****")
        self.__logger.debug(f"Current player is now player '{self.game_state.current_player_index}'")
        self.game_state = self.turn.run(self.game_state)

    def run(self):
        while True:
            try:
                self.run_one_turn()
            except GameOverException as e:
                winner_player_index = e.winner_player_index
                self.__logger.info(f"Player {winner_player_index} wins the game")
                log_directory_path = os.getenv("LOG_DIRECTORY_PATH")
                if log_directory_path:
                    results_dict = {
                        "winner_player_index": winner_player_index,
                    }
                    json_file_path = os.path.join(
                        log_directory_path,
                        f"game_{self.game_state.game_id}",
                        "results.json",
                    )
                    with open(json_file_path, "w") as json_file:
                        json.dump(results_dict, json_file, indent=4)
                break
