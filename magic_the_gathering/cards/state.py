from typing import Optional


class CardState:
    def __init__(
        self,
        is_tapped: Optional[bool] = False,
        owner_player_id: Optional[int] = 0,
        started_turn_controlled_by_player_id: Optional[int] = 0,
        damage_marked: Optional[int] = 0,
    ):
        self.is_tapped = is_tapped
        self.owner_player_id = owner_player_id
        self.started_turn_controlled_by_player_id = started_turn_controlled_by_player_id
        self.damage_marked = damage_marked

    def to_json_dict(self) -> dict:
        return {
            "is_tapped": self.is_tapped,
            "owner_player_id": self.owner_player_id,
            "started_turn_controlled_by_player_id": self.started_turn_controlled_by_player_id,
            "damage_marked": self.damage_marked,
        }
