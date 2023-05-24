from random import shuffle
from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class ShuffleAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                for zone in ZonePosition:
                    if zone != ZonePosition.STACK:
                        possible_actions.append(
                            cls(
                                owner=f"Player {player_index}",
                                zone=zone,
                                player_index=player_index,
                            )
                        )
        return possible_actions

    def __init__(
        self,
        owner: str,
        zone: ZonePosition,
        player_index: int,
    ):
        super().__init__(owner=owner)
        self.zone = zone
        self.player_index = player_index

    def _execute(self, game_state: GameState) -> GameState:
        assert self.zone != ZonePosition.STACK
        zone_to_shuffle = game_state.zones[self.zone][self.player_index]
        shuffle(zone_to_shuffle)
        return game_state
