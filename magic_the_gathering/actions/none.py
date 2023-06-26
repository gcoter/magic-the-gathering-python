from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState


class NoneAction(Action):
    def _execute(self, game_state: GameState) -> GameState:
        return game_state
