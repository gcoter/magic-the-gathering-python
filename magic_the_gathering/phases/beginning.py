from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class BeginningPhase(Phase):
    def __init__(self):
        super().__init__(name="Beginning Phase")

    def _run(self, game_state: GameState) -> GameState:
        game_state.current_player_has_played_a_land_this_turn = False
        return game_state
