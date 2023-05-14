from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatEndPhase(Phase):
    def __init__(self):
        super().__init__(name="Combat: End Phase")

    def run(self, game_state: GameState) -> GameState:
        # TODO: Implement end of combat triggers.
        return game_state
