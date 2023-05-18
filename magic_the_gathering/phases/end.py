from magic_the_gathering.phases.base import Phase


class EndPhase(Phase):
    def __init__(self):
        super().__init__(name="End Phase")

    def run(self, game_state):
        # TODO: Implement end phase triggers.
        # Below are the steps proposed by Maxime
        # until_end_of_turn_effects_end()
        # discard_to_hand_size()

        # We should also pass to next player
        # TODO: Is this the right place to do this?
        game_state.pass_to_next_player()

        return game_state
