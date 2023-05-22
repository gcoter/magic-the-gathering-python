import random
from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState
from magic_the_gathering.players.base import Player


class RandomPlayer(Player):
    def _choose_action(self, game_state: GameState, possible_actions: List[Action]) -> Action:
        return random.choice(possible_actions)
