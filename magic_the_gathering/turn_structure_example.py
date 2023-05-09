from magic_the_gathering.turn_structure.Phase import Phase, Phases

PHASES_IN_A_TURN = [e.value for e in Phases]


def simulate_game():
    while not game_is_over():
        for phase in PHASES_IN_A_TURN:
            apply_beginning_of_phase_game_effect(phase)
            if phase.players_get_priority:
                while not players_passed_priority_consecutively():
                    players_take_action()
                    if game_is_over():
                        break


def apply_beginning_of_phase_game_effect(_phase: Phase):
    match _phase:
        case Phases.UNTAP:
            untap()
        case Phases.UPKEEP:
            upkeep()
        case Phases.DRAW:
            draw()
        case Phases.DECLARE_ATTACKERS:
            declare_attackers()
        case Phases.DECLARE_BLOCKERS:
            declare_blockers()
        case Phases.DAMAGE:
            damage()
        case Phases.END_STEP:
            until_end_of_turn_effects_end()
            discard_to_hand_size()


def game_is_over() -> bool:
    return False


def untap():
    pass


def upkeep():
    pass


def draw():
    pass


def declare_attackers():
    pass


def declare_blockers():
    pass


def damage():
    pass


def until_end_of_turn_effects_end():
    pass


def discard_to_hand_size():
    pass


def players_passed_priority_consecutively():
    pass


def players_take_action():
    pass
