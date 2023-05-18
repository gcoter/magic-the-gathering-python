from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class MainPhase(Phase):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            allows_sorcery_speed_when_stack_is_empty=True,
        )

    def run(self, game_state: GameState) -> GameState:
        # TODO: Review the implementation of this method

        # Current player can play a land (only 1 per turn)
        hand_card_index = game_state.current_player.choose_land_to_play()
        if hand_card_index is not None and not game_state.current_player_has_played_a_land_this_turn:
            game_state.cast_card(player_index=game_state.current_player_index, hand_card_index=hand_card_index)
            # FIXME: Here we assumes that nothing happens between casting a land and resolving it
            game_state.resolve_top_of_the_stack()
            game_state.current_player_has_played_a_land_this_turn = True

        # Current player can cast creatures and/or sorceries
        hand_card_indices = self.current_player.choose_creatures_to_cast()
        for hand_card_index in hand_card_indices:
            game_state.cast_card(player_index=game_state.current_player_index, hand_card_index=hand_card_index)
            # FIXME: Here we assumes that nothing happens between casting a creature/sorcery and resolving it
            game_state.resolve_top_of_the_stack()

        return game_state
