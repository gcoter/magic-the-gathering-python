from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatBeginningPhase(Phase):
    def __init__(self):
        super().__init__(
            name="Combat: Beginning Phase",
        )

    def _run(self, game_state: GameState) -> GameState:
        # TODO: Implement beginning of combat triggers.
        return game_state
