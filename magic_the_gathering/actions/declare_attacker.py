from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class DeclareAttackerAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        attacker_player_index = game_state.current_player_index
        player_board = game_state.zones[ZonePosition.BOARD][attacker_player_index]
        for target_player_index, target_player in enumerate(game_state.players):
            if target_player_index != attacker_player_index and game_state.players[target_player_index].is_alive:
                for card_uuid, card in player_board.items():
                    if card.is_creature and not card.state.is_tapped and not card.state.is_summoning_sick:
                        possible_actions.append(
                            cls(
                                attacker_player_index=attacker_player_index,
                                target_player_index=target_player_index,
                                attacker_card_uuid=card_uuid,
                            )
                        )
        return possible_actions

    def __init__(
        self,
        attacker_player_index: int,
        target_player_index: int,
        attacker_card_uuid: str,
    ):
        super().__init__(
            source_player_index=attacker_player_index,
            target_player_index=target_player_index,
            target_card_uuids=[attacker_card_uuid],
        )
        self.target_player_index = target_player_index
        self.attacker_card_uuid = attacker_card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        attacker_player_index = game_state.current_player_index
        player_board = game_state.zones[ZonePosition.BOARD][attacker_player_index]
        assert self.attacker_card_uuid in player_board
        attacker_card = player_board[self.attacker_card_uuid]
        assert attacker_card.is_creature
        assert not attacker_card.state.is_tapped
        assert game_state.players[self.target_player_index].is_alive
        if self.target_player_index not in game_state.current_player_attackers:
            game_state.current_player_attackers[self.target_player_index] = []
        game_state.current_player_attackers[self.target_player_index].append(self.attacker_card_uuid)
        attacker_card.state.is_tapped = True
        return game_state
