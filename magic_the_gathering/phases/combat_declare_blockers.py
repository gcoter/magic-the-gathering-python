from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatDeclareBlockersPhase(Phase):
    def __init__(self):
        super().__init__("Combat: Declare Blockers Phase")

    def run(self, game_state: GameState) -> GameState:
        # TODO: Implement declare blockers phase.
        return game_state
