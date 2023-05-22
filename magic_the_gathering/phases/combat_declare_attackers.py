from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.declare_attacker import DeclareAttackerAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.players_get_priority import PhaseWherePlayersGetPriority


class CombatDeclareAttackersPhase(PhaseWherePlayersGetPriority):
    @staticmethod
    def list_possible_actions(game_state: GameState) -> List[Action]:
        return [None] + DeclareAttackerAction.list_possible_actions(game_state=game_state)

    def __init__(self):
        super().__init__(name="Combat: Declare Attackers Phase")

    def run(self, game_state: GameState) -> GameState:
        while True:
            possible_actions = CombatDeclareAttackersPhase.list_possible_actions(game_state)
            current_player = game_state.current_player
            action = current_player.choose_action(
                game_state=game_state,
                possible_actions=possible_actions,
            )
            if action is None:
                break
            game_state = action.execute(game_state)
        return game_state
