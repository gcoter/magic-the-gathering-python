from magic_the_gathering.game_state import GameState, ZonePosition
from magic_the_gathering.phases.base import Phase


class BeginningPhase(Phase):
    def __init__(self):
        super().__init__(name="Beginning Phase")

    def _run(self, game_state: GameState) -> GameState:
        game_state.current_player_has_played_a_land_this_turn = False
        self.__reset_summoning_sickness_flags(game_state)

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

    def __reset_summoning_sickness_flags(self, game_state: GameState) -> GameState:
        for player_index in range(game_state.n_players):
            player_board = game_state.zones[ZonePosition.BOARD][player_index]
            for permanent in player_board.values():
                permanent.state.changed_controller_this_turn = False
                # Make sure to set this changed_controller_this_turn to True when a permanent changes controller
                if player_index == game_state.current_player_index:
                    permanent.state.current_controller_started_their_last_turn_with_this_in_play = True
        return game_state
