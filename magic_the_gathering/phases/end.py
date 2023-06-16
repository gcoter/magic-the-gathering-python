from magic_the_gathering.actions.pass_to_next_player import PassToNextPlayerAction
from magic_the_gathering.game_state import ZonePosition
from magic_the_gathering.phases.base import Phase


class EndPhase(Phase):
    def __init__(self):
        super().__init__(name="End Phase")

    def _run(self, game_state):
        # TODO: Implement end phase triggers.
        # Below are the steps proposed by Maxime
        # until_end_of_turn_effects_end()
        # discard_to_hand_size()

        # Set damage to 0 for all permanents
        for player_index in range(game_state.n_players):
            player_board = game_state.zones[ZonePosition.BOARD][player_index]
            for permanent in player_board.values():
                permanent.state.damage_marked = 0

        # We should also pass to next player
        game_state = PassToNextPlayerAction().execute(game_state)

        return game_state
