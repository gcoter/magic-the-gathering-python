from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class UntapAction(Action):
    def __init__(self, owner: str, player_index: int, card_uuid: str):
        super().__init__(owner=owner)
        self.player_index = player_index
        self.card_uuid = card_uuid

    def execute(self, game_state: GameState) -> GameState:
        player_board = game_state.zones[ZonePosition.BOARD][self.player_index]
        assert self.card_uuid in player_board.keys()
        player_card = player_board[self.card_uuid]
        player_card.state.is_tapped = False
        return game_state


class UntapAllAction(Action):
    def __init__(
        self,
        owner: str,
        player_index: int,
    ):
        super().__init__(owner=owner)
        self.player_index = player_index

    def execute(self, game_state: GameState) -> GameState:
        player_board = game_state.zones[ZonePosition.BOARD][self.player_index]
        for player_card in player_board.values():
            player_card.state.is_tapped = False
        return game_state
