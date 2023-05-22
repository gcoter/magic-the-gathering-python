from magic_the_gathering.actions.deal_damage import DealDamageAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatDamagePhase(Phase):
    def __init__(self):
        super().__init__(name="Combat: Damage Phase")

    def run(self, game_state: GameState) -> GameState:
        # FIXME: We assume the blockers are already ordered as chosen by the attacker
        for deal_damage_action in DealDamageAction.list_possible_actions(game_state):
            game_state = deal_damage_action.execute(game_state)
        return game_state
