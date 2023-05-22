from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatEndPhase(Phase):
    def __init__(self):
        super().__init__(name="Combat: End Phase")

    def _run(self, game_state: GameState) -> GameState:
        # TODO: Implement end of combat triggers.

        # Reset the list of attackers and blockers
        game_state.current_player_attackers = {}
        game_state.other_players_blockers = {}

        return game_state
