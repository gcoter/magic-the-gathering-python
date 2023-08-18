from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class PutCardToBottomOfLibraryAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                for source_zone in ZonePosition:
                    if source_zone != ZonePosition.STACK:
                        player_zone = game_state.zones[source_zone][player_index]
                        for card_uuid, card in player_zone.items():
                            possible_actions.append(
                                cls(
                                    source_zone=source_zone,
                                    target_player_index=player_index,
                                    target_card_uuid=card_uuid,
                                )
                            )
        return possible_actions

    def __init__(self, source_zone: ZonePosition, target_player_index: int, target_card_uuid: str):
        super().__init__(
            source_zone=source_zone, target_player_index=target_player_index, target_card_uuids=[target_card_uuid]
        )
        self.target_card_uuid = target_card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        assert self.source_zone != ZonePosition.STACK
        player_zone = game_state.zones[self.source_zone][self.target_player_index]
        player_library = game_state.zones[ZonePosition.LIBRARY][self.target_player_index]
        assert self.target_card_uuid in player_zone
        card = player_zone[self.target_card_uuid]
        player_library[self.target_card_uuid] = card
        player_library.move_to_end(key=self.target_card_uuid, last=False)  # This should put the card at the bottom
        del player_zone[self.target_card_uuid]
        return game_state
