from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatDamagePhase(Phase):
    def __init__(self):
        super().__init__(
            name="Combat: Damage Phase",
            players_get_priority=False,
        )

    def run(self, game_state: GameState) -> GameState:
        # TODO: Implement combat damage phase.
        return game_state
