from magic_the_gathering.actions.discard import DiscardAction
from magic_the_gathering.actions.pass_to_next_player import PassToNextPlayerAction
from magic_the_gathering.game_state import GameState, ZonePosition
from magic_the_gathering.phases.base import Phase


class EndPhase(Phase):
    def __init__(self):
        super().__init__(name="End Phase")

    def _run(self, game_state: GameState):
        # TODO: Implement end phase triggers.
        # Below are the steps proposed by Maxime
        # until_end_of_turn_effects_end()

        # Discard to hand size
        game_state = self.__discard_to_hand_size(game_state)

        # Set damage to 0 for all permanents
        for player_index in range(game_state.n_players):
            player_board = game_state.zones[ZonePosition.BOARD][player_index]
            for permanent in player_board.values():
                permanent.state.damage_marked = 0

        # We should also pass to next player
        game_state = PassToNextPlayerAction().execute(game_state)

        return game_state

    def __discard_to_hand_size(self, game_state: GameState):
        target_hand_size = game_state.game_mode.initial_hand_size
        current_player_hand = game_state.zones[ZonePosition.HAND][game_state.current_player_index]
        while len(current_player_hand) > target_hand_size:
            possible_actions = [
                action
                for action in DiscardAction.list_possible_actions(game_state=game_state)
                if action.target_player_index == game_state.current_player_index
            ]
            current_player = game_state.current_player
            action = current_player.choose_action(
                game_state=game_state,
                possible_actions=possible_actions,
            )
            game_state = action.execute(game_state)
        return game_state
