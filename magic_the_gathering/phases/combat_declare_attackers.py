from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatDeclareAttackersPhase(Phase):
    def __init__(self):
        super().__init__("Combat: Declare Attackers Phase")

    def run(self, game_state: GameState) -> GameState:
        # TODO: Review this implementation. We should keep in mind that the decisions of the player should be passed to the 'CombatDeclareBlockersPhase'
        attackers_board_indices, target_player_indices = game_state.current_player.choose_attackers()
        game_state.tap_cards(player_index=game_state.current_player_index, board_indices=attackers_board_indices)
        return game_state
