from pyparsing import Optional


class CardObjectState:
    def __init__(
        self,
        is_tapped: Optional[bool] = False,
        owner_player_id: Optional[int] = 0,
        started_turn_controlled_by_player_id: Optional[int] = 0,
    ):
        self.is_tapped = is_tapped
        self.owner_player_id = owner_player_id
        self.started_turn_controlled_by_player_id = started_turn_controlled_by_player_id
