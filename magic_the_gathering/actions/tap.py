from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class TapAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                player_board = game_state.zones[ZonePosition.BOARD][player_index]
                for card_uuid, card in player_board.items():
                    if not card.state.is_tapped:
                        possible_actions.append(
                            cls(
                                owner=f"Player {player_index}",
                                player_index=player_index,
                                card_uuid=card_uuid,
                            )
                        )
        return possible_actions

    def __init__(self, owner: str, player_index: int, card_uuid: str):
        super().__init__(owner=owner)
        self.player_index = player_index
        self.card_uuid = card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        player_board = game_state.zones[ZonePosition.BOARD][self.player_index]
        assert self.card_uuid in player_board.keys()
        player_card = player_board[self.card_uuid]
        # FIXME: Increase mana pool if land
        assert not player_card.state.is_tapped
        player_card.state.is_tapped = True
        return game_state
