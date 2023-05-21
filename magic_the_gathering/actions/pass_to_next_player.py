from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class PassToNextPlayerAction(Action):
    def execute(self, game_state: GameState) -> GameState:
        game_state.current_player_index = (game_state.current_player_index + 1) % game_state.n_players
        return game_state
