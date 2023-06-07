import logging
from abc import abstractmethod
from typing import List

from magic_the_gathering.game_state import GameState


class Action:
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
        game_state = self._execute(game_state)
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
