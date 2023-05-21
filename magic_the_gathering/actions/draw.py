from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class DrawAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                player_library = game_state.zones[ZonePosition.LIBRARY][player_index]
                if len(player_library) > 0:
                    possible_actions.append(
                        cls(
                            owner=f"Player {player_index}",
                            player_index=player_index,
                        )
                    )
        return possible_actions

    def __init__(
        self,
        owner: str,
        player_index: int,
    ):
        super().__init__(owner=owner)
        self.player_index = player_index

    def _execute(self, game_state: GameState) -> GameState:
        player_library = game_state.zones[ZonePosition.LIBRARY][self.player_index]
        player_hand = game_state.zones[ZonePosition.HAND][self.player_index]
        assert len(player_library) > 0
        drawn_card = player_library.pop(0)
        player_hand[drawn_card.uuid] = drawn_card
        return game_state
