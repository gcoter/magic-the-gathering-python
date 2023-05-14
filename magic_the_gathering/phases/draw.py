from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class DrawPhase(Phase):
    def __init__(self):
        super().__init__(name="Draw Phase")

    def run(self, game_state: GameState) -> GameState:
        game_state.draw_cards_from_deck(
            player_index=game_state.current_player_index,
            n_cards=1,
        )
        return game_state
