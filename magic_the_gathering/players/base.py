from typing import Dict


class Player:
    def __init__(
        self,
        life_points: int = 20,
        mana_pool: Dict[str, int] = None,
    ):
        self.life_points = life_points
        self.mana_pool = mana_pool
        if self.mana_pool is None:
            self.mana_pool = {
                "white": 0,
                "blue": 0,
                "black": 0,
                "red": 0,
                "green": 0,
            }
