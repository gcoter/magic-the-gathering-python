from typing import Optional

import numpy as np


class CardState:
    def __init__(
        self,
        is_tapped: Optional[bool] = False,
        owner_player_id: Optional[int] = 0,
        current_controller_started_their_last_turn_with_this_in_play: Optional[bool] = False,
        changed_controller_this_turn: Optional[bool] = False,
        damage_marked: Optional[int] = 0,
    ):
        self.is_tapped = is_tapped
        self.owner_player_id = owner_player_id
        self.current_controller_started_their_last_turn_with_this_in_play = (
            current_controller_started_their_last_turn_with_this_in_play
        )
        self.changed_controller_this_turn = changed_controller_this_turn
        self.damage_marked = damage_marked

    @property
    def is_summoning_sick(self) -> bool:
        return (
            not self.current_controller_started_their_last_turn_with_this_in_play or self.changed_controller_this_turn
        )

    def to_json_dict(self) -> dict:
        return {
            "is_tapped": self.is_tapped,
            "owner_player_id": self.owner_player_id,
            "current_controller_started_their_last_turn_with_this_in_play": self.current_controller_started_their_last_turn_with_this_in_play,
            "changed_controller_this_turn": self.changed_controller_this_turn,
            "damage_marked": self.damage_marked,
        }

    def __repr__(self):
        return f"CardState(is_tapped={self.is_tapped}, owner_player_id={self.owner_player_id}, is_summoning_sick={self.is_summoning_sick}, damage_marked={self.damage_marked})"

    def __str__(self) -> str:
        return self.__repr__()

    def to_vector(self) -> np.ndarray:
        return np.array(
            [
                self.is_tapped,
                self.damage_marked,
                self.is_summoning_sick,
            ]
        )
