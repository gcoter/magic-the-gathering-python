from magic_the_gathering.actions.untap import UntapAllAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class UntapPhase(Phase):
    def __init__(self):
        super().__init__(name="Untap Phase")

    def run(self, game_state: GameState) -> GameState:
        action = UntapAllAction(owner="game", player_index=game_state.current_player_index)
        return action.execute(game_state)
