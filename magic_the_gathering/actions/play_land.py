from magic_the_gathering.actions.base import Action
from magic_the_gathering.cards.state import CardState
from magic_the_gathering.game_state import GameState, ZonePosition


class PlayLandAction(Action):
    def __init__(
        self,
        owner: str,
        player_index: int,
        land_card_uuid: str,
    ):
        super().__init__(owner=owner)
        self.player_index = player_index
        self.land_card_uuid = land_card_uuid

    def execute(self, game_state: GameState) -> GameState:
        player_hand = game_state.zones[ZonePosition.HAND][self.player_index]
        player_board = game_state.zones[ZonePosition.BOARD][self.player_index]
        assert self.land_card_uuid in player_hand.keys()
        player_land_card = player_hand[self.land_card_uuid]
        assert player_land_card.is_land
        assert not game_state.current_player_has_played_a_land_this_turn
        player_land_card_new_instance = player_land_card.create_new_instance(
            state=CardState(
                tapped=False,
                owner_player_id=self.player_index,
                started_turn_controlled_by_player_id=self.player_index,
            )
        )
        del player_hand[self.land_card_uuid]
        player_board[player_land_card_new_instance.uuid] = player_land_card_new_instance
        game_state.current_player_has_played_a_land_this_turn = True
        return game_state
