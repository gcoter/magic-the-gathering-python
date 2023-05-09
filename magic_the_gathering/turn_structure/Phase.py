from enum import Enum


class Phase:
    def __init__(
        self,
        name: str,
        allows_sorcery_speed_when_stack_is_empty: bool = False,
        players_get_priority: bool = True,
    ):
        self.name = name
        self.allows_sorcery_speed_when_stack_is_empty = allows_sorcery_speed_when_stack_is_empty
        self.players_get_priority = players_get_priority


class Phases(Enum):
    UNTAP = Phase(name="untap", players_get_priority=False)
    UPKEEP = Phase(name="upkeep")
    DRAW = Phase(name="draw")
    MAIN_PHASE_1 = Phase(name="main phase 1", allows_sorcery_speed_when_stack_is_empty=True)
    BEGINNING_OF_COMBAT = Phase(name="beginning of combat")
    DECLARE_ATTACKERS = Phase(name="declare attackers")
    DECLARE_BLOCKERS = Phase(name="declare blockers")
    DAMAGE = Phase(name="damage", players_get_priority=False)
    END_OF_COMBAT = Phase(name="end of combat")
    MAIN_PHASE_2 = Phase(name="main phase 2", allows_sorcery_speed_when_stack_is_empty=True)
    END_STEP = Phase(name="end step")
