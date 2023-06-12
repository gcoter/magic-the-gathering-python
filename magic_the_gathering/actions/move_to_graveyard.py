from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class MoveToGraveyardAction(Action):
    def __init__(self, source_player_index, target_player_index: int, target_card_uuid: str):
        super().__init__(
            source_player_index=source_player_index,
            target_player_index=target_player_index,
            target_card_uuids=[target_card_uuid],
        )
        self.target_card_uuid = target_card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        self.logger.info(f"Move card {self.target_card_uuid} of Player {self.target_player_index} to graveyard")
        assert self.target_card_uuid in game_state.zones[ZonePosition.BOARD][self.target_player_index]
        card = game_state.zones[ZonePosition.BOARD][self.target_player_index][self.target_card_uuid]
        card_new_instance = card.create_new_instance()
        game_state.zones[ZonePosition.GRAVEYARD][self.target_player_index][card_new_instance.uuid] = card_new_instance
        del game_state.zones[ZonePosition.BOARD][self.target_player_index][self.target_card_uuid]
        return game_state
