from typing import List, Tuple, Union

from magic_the_gathering.game_state import GameState


class Player:
    def __init__(
        self,
        life_points: int = 20,
    ):
        self.life_points = life_points

    def choose_mulligan(self, game_state: GameState) -> bool:
        pass

    def choose_land_to_play(self) -> Union[int, None]:
        pass

    def choose_creatures_to_cast(self) -> List[int]:
        pass

    def choose_artifacts_to_cast(self):
        pass

    def choose_enchantment_to_cast(self):
        pass

    def choose_sorceries_to_cast(self):
        pass

    def choose_instants_to_cast(self):
        pass

    def choose_attackers(self) -> Tuple[List[int], List[int]]:
        pass

    def choose_blockers(self) -> Tuple[List[int], List[int]]:
        pass
