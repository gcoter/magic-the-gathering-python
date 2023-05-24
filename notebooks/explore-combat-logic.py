import itertools
from dataclasses import dataclass
from typing import List

from toolz.curried import compose_left, curry, filter, map

# Finding possible attack options


@dataclass
class CreatureAttackingAPlayer:
    attacker: str
    player: str


def compute_attacker_declaration_options(
    players: List[str], creatures_active_player_controls: List[str]
) -> List[CreatureAttackingAPlayer]:
    return compose_left(
        map(get_players_this_creature_can_attack(players)),
        lambda possibilities_for_each_creature: itertools.product(*possibilities_for_each_creature),
        map(filter(lambda creature_attacking_a_player: creature_attacking_a_player.player != "no one")),
        map(list),
        list,
        # TODO: should probably group by player like the blocker declaration options group by attackers
    )(creatures_active_player_controls)


@curry
def get_players_this_creature_can_attack(players, active_player_creature):
    return [
        CreatureAttackingAPlayer(active_player_creature, player)
        for player in filter_players_creature_can_attack(active_player_creature, players)
    ] + [CreatureAttackingAPlayer(active_player_creature, "no one")]


def filter_players_creature_can_attack(creature, players):
    # TODO
    return players


attacker_declaration_options = compute_attacker_declaration_options(
    players=[f"player_{i}" for i in range(1, 4)],
    creatures_active_player_controls=[f"attacker_{i}" for i in range(1, 4)],
)
print(len(attacker_declaration_options))


# Defending from the perspective of one player


@dataclass
class CreatureBlockingAnAttacker:
    attacker: str
    blocker: str


@dataclass
class SubBattle:
    attacker: str
    blockers: [str]


def compute_blocker_declaration_options(
    creatures_attacking_me: List[str], my_creatures: List[str]
) -> List[List[SubBattle]]:
    return compose_left(
        map(get_attackers_this_creature_can_block(creatures_attacking_me)),
        lambda possibilities_for_each_creature: itertools.product(*possibilities_for_each_creature),
        map(filter(lambda creature_blocking_attacker: creature_blocking_attacker.attacker != "no one")),
        map(list),
        map(as_sub_battles),
        map(filter(is_sub_battle_legal)),
        map(list),
        list,
    )(my_creatures)


@curry
def get_attackers_this_creature_can_block(attackers, defending_player_creature):
    return [
        CreatureBlockingAnAttacker(attacker, defending_player_creature)
        for attacker in filter_attackers_this_creature_can_block(attackers, defending_player_creature)
    ] + [CreatureBlockingAnAttacker("no one", defending_player_creature)]


def filter_attackers_this_creature_can_block(attackers, defending_player_creature):
    # TODO
    return attackers


def as_sub_battles(blocker_declaration_option: [CreatureBlockingAnAttacker]) -> List[SubBattle]:
    def get_attacker(creature_blocking_an_attacker: CreatureBlockingAnAttacker):
        return creature_blocking_an_attacker.attacker

    return [
        SubBattle(attacker, [blocker_object.blocker for blocker_object in blocker_objects])
        for attacker, blocker_objects in itertools.groupby(
            sorted(blocker_declaration_option, key=get_attacker),
            get_attacker,
        )
    ]


def is_sub_battle_legal(sub_battle: SubBattle) -> bool:
    # TODO check if this subBattle is legal regarding stuff like menace
    return True


creatures_attacking_me = [f"attacker_{i}" for i in range(1, 4)]
my_creatures = [f"blocker_{i}" for i in range(1, 4)]

blocker_declaration_option = compute_blocker_declaration_options(
    creatures_attacking_me=[f"attacker_{i}" for i in range(1, 4)],
    my_creatures=[f"blocker_{i}" for i in range(1, 4)],
)
print(len(blocker_declaration_option))
