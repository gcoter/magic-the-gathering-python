from magic_the_gathering.actions.draw import DrawAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class DrawPhase(Phase):
    def __init__(self):
        super().__init__(name="Draw Phase")

    def _run(self, game_state: GameState) -> GameState:
        action = DrawAction(player_index=game_state.current_player_index)
        return action.execute(game_state)
