from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class PassToNextPlayerAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        return [cls(owner="Game")]

    def _execute(self, game_state: GameState) -> GameState:
        while True:
            game_state.current_player_index = (game_state.current_player_index + 1) % game_state.n_players
            if game_state.players[game_state.current_player_index].is_alive:
                break
        return game_state
