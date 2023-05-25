from dataclasses import dataclass
from typing import Dict


@dataclass
class GameMode:
    # TODO: Are these attributes sufficient to define a game mode?
    name: str
    initial_life_points: int
    initial_hand_size: int

    def to_json_dict(self) -> Dict:
        return {
            "name": self.name,
            "initial_life_points": self.initial_life_points,
            "initial_hand_size": self.initial_hand_size,
        }
