from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class UntapPhase(Phase):
    def __init__(self):
        super().__init__(
            name="Untap Phase",
            players_get_priority=False,
        )

    def run(self, game_state: GameState) -> GameState:
        game_state.untap_all_permanents(player_index=game_state.current_player_index)
        return game_state
