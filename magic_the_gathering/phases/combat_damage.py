from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatDamagePhase(Phase):
    def __init__(self):
        super().__init__(name="Combat: Damage Phase")

    def run(self, game_state: GameState) -> GameState:
        # We assume the blockers are already ordered as chosen by the attacker
        return game_state
