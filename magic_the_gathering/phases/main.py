from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.cast_card import CastCardAction
from magic_the_gathering.actions.play_land import PlayLandAction
from magic_the_gathering.actions.resolve_stack import ResolveTopOfStackAction
from magic_the_gathering.actions.tap import TapAction
from magic_the_gathering.game_state import GameState, ZonePosition
from magic_the_gathering.phases.players_get_priority import PhaseWherePlayersGetPriority


class MainPhase(PhaseWherePlayersGetPriority):
    @staticmethod
    def list_possible_actions(game_state: GameState) -> List[Action]:
        possible_actions = [None]
        possible_actions.extend(
            [
                action
                for action in PlayLandAction.list_possible_actions(game_state)
                if action.player_index == game_state.current_player_index
            ]
        )
        possible_actions.extend(
            [
                action
                for action in CastCardAction.list_possible_actions(game_state)
                if action.player_index == game_state.current_player_index
            ]
        )
        possible_actions.extend(
            [
                action
                for action in TapAction.list_possible_actions(game_state)
                if action.player_index == game_state.current_player_index
            ]
        )
        return possible_actions

    def __init__(self, name: str):
        super().__init__(
            name=name,
            allows_sorcery_speed_when_stack_is_empty=True,
        )

    def _run(self, game_state: GameState) -> GameState:
        while True:
            # Current player chooses one action
            possible_actions = MainPhase.list_possible_actions(game_state)
            current_player = game_state.current_player
            action = current_player.choose_action(
                game_state=game_state,
                possible_actions=possible_actions,
            )
            if action is None:
                break
            game_state = action.execute(game_state)

            # TODO: Other players can respond to the action

            # Resolve the stack
            # TODO: Is it correct to resolve the whole stack at once?
            while len(game_state.zones[ZonePosition.STACK]) > 0:
                game_state = ResolveTopOfStackAction().execute(game_state)

        return game_state
