from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.declare_attacker import DeclareAttackerAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.players_get_priority import PhaseWherePlayersGetPriority


class CombatDeclareAttackersPhase(PhaseWherePlayersGetPriority):
    @staticmethod
    def list_possible_actions(game_state: GameState) -> List[Action]:
        return [None] + DeclareAttackerAction.list_possible_actions(game_state=game_state)

    def __init__(self, force_combat: bool = False):
        super().__init__(name="Combat: Declare Attackers Phase")
        self.force_combat = force_combat

    def _run(self, game_state: GameState) -> GameState:
        n_attackers = 0
        while True:
            possible_actions = CombatDeclareAttackersPhase.list_possible_actions(game_state)
            current_player = game_state.current_player
            action = current_player.choose_action(
                game_state=game_state,
                possible_actions=possible_actions,
            )
            if action is not None:
                n_attackers += 1
            if n_attackers == 0 and self.force_combat and action is None and possible_actions != [None]:
                while action is None:
                    action = current_player.choose_action(
                        game_state=game_state,
                        possible_actions=possible_actions,
                    )
            if action is None:
                break
            game_state = action.execute(game_state)
        return game_state
