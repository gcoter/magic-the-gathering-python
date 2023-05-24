from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.declare_blocker import DeclareBlockerAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.players_get_priority import PhaseWherePlayersGetPriority


class CombatDeclareBlockersPhase(PhaseWherePlayersGetPriority):
    @staticmethod
    def list_possible_actions(game_state: GameState) -> List[Action]:
        return [None] + DeclareBlockerAction.list_possible_actions(game_state=game_state)

    def __init__(self, force_combat: bool = False):
        super().__init__(name="Combat: Declare Blockers Phase")
        self.force_combat = force_combat

    def _run(self, game_state: GameState) -> GameState:
        for blocker_player_index in game_state.current_player_attackers.keys():
            blocker_player = game_state.players[blocker_player_index]
            assert blocker_player.is_alive
            n_blockers = 0
            while True:
                possible_actions = [
                    action
                    for action in CombatDeclareBlockersPhase.list_possible_actions(game_state)
                    if action is None or action.blocker_player_index == blocker_player_index
                ]
                action = blocker_player._choose_action(
                    game_state=game_state,
                    possible_actions=possible_actions,
                )
                if action is not None:
                    n_blockers += 1
                if n_blockers == 0 and self.force_combat and action is None and possible_actions != [None]:
                    while action is None:
                        action = blocker_player.choose_action(
                            game_state=game_state,
                            possible_actions=possible_actions,
                        )
                if action is None:
                    break
            for attacker_card_uuid in game_state.current_player_attackers[blocker_player_index]:
                if blocker_player_index not in game_state.other_players_blockers:
                    game_state.other_players_blockers[blocker_player_index] = {}
                if attacker_card_uuid not in game_state.other_players_blockers[blocker_player_index]:
                    game_state.other_players_blockers[blocker_player_index][attacker_card_uuid] = []
        return game_state
