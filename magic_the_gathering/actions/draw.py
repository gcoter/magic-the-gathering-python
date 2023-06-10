from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.kill_player import KillPlayerAction
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
                            player_index=player_index,
                        )
                    )
        return possible_actions

    def __init__(
        self,
        player_index: int,
    ):
        super().__init__(
            target_player_index=player_index,
        )
        self.player_index = player_index

    def _execute(self, game_state: GameState) -> GameState:
        player_library = game_state.zones[ZonePosition.LIBRARY][self.player_index]
        player_hand = game_state.zones[ZonePosition.HAND][self.player_index]
        if len(player_library) == 0:
            self.logger.debug(f"Player {self.player_index} has no cards in library")
            game_state = KillPlayerAction(
                player_index=self.player_index,
            ).execute(game_state)
        else:
            _, drawn_card = player_library.popitem()
            self.logger.debug(f"Player {self.player_index} draws {drawn_card}")
            player_hand[drawn_card.uuid] = drawn_card
        return game_state
