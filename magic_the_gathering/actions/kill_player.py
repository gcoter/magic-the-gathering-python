from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class KillPlayerAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                possible_actions.append(cls(owner="Game", player_index=player_index))
        return possible_actions

    def __init__(self, owner: str, player_index: int):
        super().__init__(owner)
        self.player_index = player_index

    def _execute(self, game_state: GameState) -> GameState:
        self.logger.info(f"Player {self.player_index} is killed")
        killed_player = game_state.players[self.player_index]
        assert killed_player.is_alive
        killed_player.is_alive = False
        return game_state
