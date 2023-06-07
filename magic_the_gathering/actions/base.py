import json
import logging
import os
from abc import abstractmethod
from pathlib import Path
from typing import List

from magic_the_gathering.game_state import GameState


class Action:
    GLOBAL_ACTION_COUNT = 0

    @classmethod
    @abstractmethod
    def list_possible_actions(cls, game_state: GameState) -> List["Action"]:
        raise NotImplementedError

    def __init__(
        self,
        owner: str,
    ):
        self.owner = owner
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _execute(self, game_state: GameState) -> GameState:
        raise NotImplementedError

    def execute(self, game_state: GameState) -> GameState:
        self.logger.debug(f"Executing action: {self}")
        # input(f"Press enter to continue...")
        self.maybe_save_data_as_json(game_state)
        game_state = self._execute(game_state)
        Action.GLOBAL_ACTION_COUNT += 1
        game_state.action_history.append(self)
        game_state.check_if_game_is_over()
        return game_state

    def __str__(self) -> str:
        string = f"{self.__class__.__name__}("
        attribute_strings = [
            f"{attribute_name}={attribute_value}"
            for attribute_name, attribute_value in self.__dict__.items()
            if attribute_name != "logger"
        ]
        string += ", ".join(attribute_strings)
        string += ")"
        return string

    def __repr__(self) -> str:
        return self.__str__()

    def to_json_dict(self) -> dict:
        return {
            "action_type": self.__class__.__name__,
            "action_attributes": {
                attribute_name: attribute_value
                for attribute_name, attribute_value in self.__dict__.items()
                if attribute_name != "logger"
            },
        }

    def maybe_save_data_as_json(self, game_state: GameState):
        log_directory_path = os.getenv("LOG_DIRECTORY_PATH")
        if log_directory_path is not None:
            json_dict = {
                "game_state": game_state.to_json_dict(),
                "action": self.to_json_dict(),
            }
            json_file_path = os.path.join(
                log_directory_path,
                f"game_{game_state.game_id}",
                f"action_{Action.GLOBAL_ACTION_COUNT}.json",
            )
            Path(json_file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(json_file_path, "w") as json_file:
                json.dump(json_dict, json_file, indent=4)
