from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class UpkeepPhase(Phase):
    def __init__(self):
        super().__init__(name="Upkeep Phase")

    def _run(self, game_state: GameState) -> GameState:
        # TODO: Implement upkeep triggers.
        return game_state
