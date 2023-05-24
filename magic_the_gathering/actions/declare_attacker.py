from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class DeclareAttackerAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        attacker_player_index = game_state.current_player_index
        player_board = game_state.zones[ZonePosition.BOARD][attacker_player_index]
        for target_player_index, target_player in enumerate(game_state.other_players):
            for card_uuid, card in player_board.items():
                if card.is_creature and not card.state.is_tapped:
                    possible_actions.append(
                        cls(
                            owner=f"Player {attacker_player_index}",
                            target_player_index=target_player_index,
                            attacker_card_uuid=card_uuid,
                        )
                    )
        return possible_actions

    def __init__(
        self,
        owner: str,
        target_player_index: int,
        attacker_card_uuid: str,
    ):
        super().__init__(owner=owner)
        self.target_player_index = target_player_index
        self.attacker_card_uuid = attacker_card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        attacker_player_index = game_state.current_player_index
        player_board = game_state.zones[ZonePosition.BOARD][attacker_player_index]
        assert self.attacker_card_uuid in player_board
        attacker_card = player_board[self.attacker_card_uuid]
        assert attacker_card.is_creature
        assert not attacker_card.state.is_tapped
        if self.target_player_index not in game_state.current_player_attackers:
            game_state.current_player_attackers[self.target_player_index] = []
        game_state.current_player_attackers[self.target_player_index].append(self.attacker_card_uuid)
        attacker_card.state.is_tapped = True
        return game_state
