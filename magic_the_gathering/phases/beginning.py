from magic_the_gathering.game_state import GameState, ZonePosition
from magic_the_gathering.phases.base import Phase


class BeginningPhase(Phase):
    def __init__(self):
        super().__init__(name="Beginning Phase")

    def _run(self, game_state: GameState) -> GameState:
        game_state.current_player_has_played_a_land_this_turn = False
        self.logger.debug(
            f"Current player's hand: {game_state.zones[ZonePosition.HAND][game_state.current_player_index]}"
        )
        self.logger.debug(
            f"Current player's board: {game_state.zones[ZonePosition.BOARD][game_state.current_player_index]}"
        )
        self.logger.debug(
            f"Current player's graveyard: {game_state.zones[ZonePosition.GRAVEYARD][game_state.current_player_index]}"
        )
        return game_state
