from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class TakeMulliganAction(Action):
    def __init__(self, source_player_index: int):
        super().__init__(source_player_index=source_player_index)

    def _execute(self, game_state: GameState) -> GameState:
        return game_state
