from dataclasses import dataclass


@dataclass
class GameMode:
    # TODO: Are these attributes sufficient to define a game mode?
    name: str
    initial_life_points: int
    initial_hand_size: int
