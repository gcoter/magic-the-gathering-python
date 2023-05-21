from random import shuffle

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class ShuffleAction(Action):
    def __init__(
        self,
        owner: str,
        zone: ZonePosition,
        player_index: int,
    ):
        super().__init__(owner=owner)
        self.zone = zone
        self.player_index = player_index

    def execute(self, game_state: GameState) -> GameState:
        zone_to_shuffle = game_state.zones[self.zone]
        if self.zone != ZonePosition.STACK:
            zone_to_shuffle = zone_to_shuffle[self.player_index]
        shuffle(zone_to_shuffle)
        return game_state
