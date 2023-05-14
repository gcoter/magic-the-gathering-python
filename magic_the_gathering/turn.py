from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.combat_beginning import CombatBeginningPhase
from magic_the_gathering.phases.combat_damage import CombatDamagePhase
from magic_the_gathering.phases.combat_declare_attackers import CombatDeclareAttackersPhase
from magic_the_gathering.phases.combat_declare_blockers import CombatDeclareBlockersPhase
from magic_the_gathering.phases.combat_end import CombatEndPhase
from magic_the_gathering.phases.draw import DrawPhase
from magic_the_gathering.phases.end import EndPhase
from magic_the_gathering.phases.main import MainPhase
from magic_the_gathering.phases.untap import UntapPhase
from magic_the_gathering.phases.upkeep import UpkeepPhase


class Turn:
    def __init__(self):
        self.__phases = [
            UntapPhase(),
            UpkeepPhase(),
            DrawPhase(),
            MainPhase(name="Main Phase 1"),
            CombatBeginningPhase(),
            CombatDeclareAttackersPhase(),
            CombatDeclareBlockersPhase(),
            CombatDamagePhase(),
            CombatEndPhase(),
            MainPhase(name="Main Phase 2"),
            EndPhase(),
        ]
        # TODO: Add a logger

    def run(self, game_state: GameState) -> GameState:
        for phase in self.__phases:
            game_state = phase.run(game_state)
            # TODO: Here is the logic of a turn below, how can we implement it using the Phase classes efficiently?
            # TODO: players_get_priority seems to condition the behavior of the phase, should we consider having a different parent class for these?
            # apply_beginning_of_phase_game_effect(phase)
            # if phase.players_get_priority:
            #     while not players_passed_priority_consecutively():
            #         players_take_action()
            #         if game_is_over():
            #             break
        return game_state
