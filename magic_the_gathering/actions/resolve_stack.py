from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class ResolveTopOfStackAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        stack = game_state.zones[ZonePosition.STACK]
        if len(stack) > 0:
            return [cls()]
        return []

    def _execute(self, game_state: GameState) -> GameState:
        stack = game_state.zones[ZonePosition.STACK]
        assert len(stack) > 0
        resolved_card_uuid = next(reversed(stack))
        resolved_card = stack[resolved_card_uuid]
        del stack[resolved_card_uuid]
        if resolved_card.is_permanent:
            assert resolved_card.state is not None
            player_board = game_state.zones[ZonePosition.BOARD][resolved_card.state.owner_player_id]
            player_board[resolved_card.uuid] = resolved_card
        else:
            # FIXME: Implement resolving non-permanent cards
            raise NotImplementedError
        return game_state
