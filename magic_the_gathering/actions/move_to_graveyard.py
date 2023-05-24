from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class MoveToGraveyardAction(Action):
    def __init__(self, owner: str, player_index: int, card_uuid: str):
        super().__init__(owner)
        self.player_index = player_index
        self.card_uuid = card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        assert self.card_uuid in game_state.zones[ZonePosition.BOARD][self.player_index]
        card = game_state.zones[ZonePosition.BOARD][self.player_index][self.card_uuid]
        card_new_instance = card.create_new_instance()
        game_state.zones[ZonePosition.GRAVEYARD][self.player_index][card_new_instance.uuid] = card_new_instance
        del game_state.zones[ZonePosition.BOARD][self.player_index][self.card_uuid]
        return game_state
