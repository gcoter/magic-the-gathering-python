from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class DiscardAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                player_hand = game_state.zones[ZonePosition.HAND][player_index]
                for card_uuid, card in player_hand.items():
                    possible_actions.append(
                        cls(
                            target_player_index=player_index,
                            target_card_uuid=card_uuid,
                        )
                    )
        return possible_actions

    def __init__(self, target_player_index: int, target_card_uuid: str):
        super().__init__(
            target_player_index=target_player_index,
            target_card_uuids=[target_card_uuid],
        )
        self.target_card_uuid = target_card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        assert self.target_card_uuid in game_state.zones[ZonePosition.HAND][self.target_player_index]
        card = game_state.zones[ZonePosition.HAND][self.target_player_index][self.target_card_uuid]
        card_new_instance = card.create_new_instance()
        game_state.zones[ZonePosition.GRAVEYARD][self.target_player_index][card_new_instance.uuid] = card_new_instance
        del game_state.zones[ZonePosition.HAND][self.target_player_index][self.target_card_uuid]
        return game_state
