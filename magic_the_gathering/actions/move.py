from magic_the_gathering.actions.base import Action
from magic_the_gathering.cards.state import CardState
from magic_the_gathering.game_state import GameState, ZonePosition


class MoveAction(Action):
    def __init__(
        self,
        owner: str,
        from_zone: str,
        to_zone: str,
        from_player_index: int,
        to_player_index: int,
        card_uuid: str,
        create_new_instance: bool = False,
    ):
        super().__init__(owner=owner)
        self.from_zone = from_zone
        self.to_zone = to_zone
        self.from_player_index = from_player_index
        self.to_player_index = to_player_index
        self.card_uuid = card_uuid
        self.create_new_instance = create_new_instance

    def execute(self, game_state: GameState) -> GameState:
        from_zone = game_state.zones[self.from_zone]
        to_zone = game_state.zones[self.to_zone]
        if self.from_zone != ZonePosition.STACK:
            from_zone = from_zone[self.from_player_index]
        if self.to_zone != ZonePosition.STACK:
            to_zone = to_zone[self.to_player_index]
        card = from_zone[self.card_uuid]
        del from_zone[self.card_uuid]
        if self.create_new_instance:
            card = card.create_new_instance(state=CardState() if card.is_permament is not None else None)
        to_zone[card.uuid] = card
        return game_state
