from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.declare_attacker import DeclareAttackerAction
from magic_the_gathering.actions.none import NoneAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.players_get_priority import PhaseWherePlayersGetPriority


class CombatDeclareAttackersPhase(PhaseWherePlayersGetPriority):
    @staticmethod
    def list_possible_actions(game_state: GameState) -> List[Action]:
        return [
            NoneAction(source_player_index=game_state.current_player_index)
        ] + DeclareAttackerAction.list_possible_actions(game_state=game_state)

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
            if not isinstance(action, NoneAction):
                n_attackers += 1
            if (
                n_attackers == 0
                and self.force_combat
                and isinstance(action, NoneAction)
                and possible_actions != [NoneAction(source_player_index=game_state.current_player_index)]
            ):
                while isinstance(action, NoneAction):
                    action = current_player.choose_action(
                        game_state=game_state,
                        possible_actions=possible_actions,
                    )
            game_state = action.execute(game_state)
            if isinstance(action, NoneAction):
                break

        self.logger.info(f"Declared attackers: {game_state.current_player_attackers}")
        return game_state
