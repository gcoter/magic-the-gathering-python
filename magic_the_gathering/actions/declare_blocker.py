from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class DeclareBlockerAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for blocker_player_index, attacker_card_uuids in game_state.current_player_attackers.items():
            for blocker_card_uuid, blocker_card in game_state.zones[ZonePosition.BOARD][blocker_player_index].items():
                if blocker_card.is_creature and not blocker_card.state.is_tapped:
                    for attacker_card_uuid in attacker_card_uuids:
                        possible_actions.append(
                            cls(
                                owner=f"Player {blocker_player_index}",
                                blocker_player_index=blocker_player_index,
                                blocker_card_uuid=blocker_card_uuid,
                                attacker_card_uuid=attacker_card_uuid,
                            )
                        )
        return possible_actions

    def __init__(self, owner: str, blocker_player_index: int, blocker_card_uuid: str, attacker_card_uuid: str):
        super().__init__(owner=owner)
        self.blocker_player_index = blocker_player_index
        self.blocker_card_uuid = blocker_card_uuid
        self.attacker_card_uuid = attacker_card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        blocker_board = game_state.zones[ZonePosition.BOARD][self.blocker_player_index]
        assert self.blocker_card_uuid in blocker_board
        blocker_card = blocker_board[self.blocker_card_uuid]
        assert blocker_card.is_creature
        assert not blocker_card.is_tapped
        assert self.attacker_card_uuid in game_state.current_player_attackers[self.blocker_player_index]
        if self.blocker_player_index not in game_state.other_players_blockers:
            game_state.other_players_blockers[self.blocker_player_index] = {}
        if self.attacker_card_uuid not in game_state.other_players_blockers[self.blocker_player_index]:
            game_state.other_players_blockers[self.blocker_player_index][self.attacker_card_uuid] = []
        game_state.other_players_blockers[self.blocker_player_index][self.attacker_card_uuid].append(
            self.blocker_card_uuid
        )
        blocker_card.is_tapped = True
        return game_state
