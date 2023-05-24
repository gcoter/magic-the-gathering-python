from magic_the_gathering.actions.deal_damage import DealDamageAction
from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class CombatDamagePhase(Phase):
    def __init__(self):
        super().__init__(name="Combat: Damage Phase")

    def _run(self, game_state: GameState) -> GameState:
        # FIXME: I think we should add a phase before this one to allow the attacker to choose the order of blockers
        for deal_damage_action in DealDamageAction.list_possible_actions(game_state):
            game_state = deal_damage_action.execute(game_state)
        return game_state
