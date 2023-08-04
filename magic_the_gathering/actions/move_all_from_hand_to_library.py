from collections import OrderedDict
from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class MoveAllFromHandToLibraryAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                possible_actions.append(cls(target_player_index=player_index))
        return possible_actions

    def __init__(self, target_player_index: int):
        super().__init__(target_player_index=target_player_index)

    def _execute(self, game_state: GameState) -> GameState:
        player_hand = game_state.zones[ZonePosition.HAND][self.target_player_index]
        player_library = game_state.zones[ZonePosition.LIBRARY][self.target_player_index]
        assert len(player_hand) > 0

        # Add cards from hand to library
        for card_uuid, card in player_hand.items():
            player_library[card_uuid] = card

        # Empty hand
        game_state.zones[ZonePosition.HAND][self.target_player_index] = OrderedDict()

        return game_state
