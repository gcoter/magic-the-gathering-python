import logging
import os
import pickle
from pathlib import Path

from magic_the_gathering.actions.base import Action
from magic_the_gathering.exceptions import GameOverException
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.mulligan import MulliganPhase
from magic_the_gathering.turn import Turn


class GameEngine:
    def __init__(self, game_state: GameState, log_directory_path: str = None):
        self.game_state = game_state
        self.log_directory_path = log_directory_path

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
                if self.log_directory_path:
                    data_dict = {
                        "game_id": self.game_state.game_id,
                        "player_datasets": [
                            self.game_state.players[player_index].dataset
                            for player_index in range(self.game_state.n_players)
                        ],
                        "winner_player_index": winner_player_index,
                    }
                    pickle_file_path = os.path.join(self.log_directory_path, f"game_{self.game_state.game_id}.pickle")
                    print(f"Write data to '{pickle_file_path}'")
                    Path(self.log_directory_path).mkdir(parents=True, exist_ok=True)
                    with open(pickle_file_path, "wb") as f:
                        pickle.dump(data_dict, f)
                return winner_player_index
