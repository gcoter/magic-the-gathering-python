from magic_the_gathering.actions.base import Action
from magic_the_gathering.cards.state import CardState
from magic_the_gathering.game_state import GameState, ZonePosition


class CastCardAction(Action):
    def __init__(self, owner: str, player_index: int, card_uuid: str):
        super().__init__(owner=owner)
        self.player_index = player_index
        self.card_uuid = card_uuid

    def execute(self, game_state: GameState) -> GameState:
        player_hand = game_state.zones[ZonePosition.HAND][self.player_index]
        stack = game_state.zones[ZonePosition.STACK]

        assert self.card_uuid in player_hand.keys()
        player_card = player_hand[self.card_uuid]
        assert not player_card.is_land

        # Handle mana cost
        player_mana_pool = game_state.players[self.player_index].mana_pool
        for mana_color, mana_cost in player_card.mana_cost_dict.items():
            # FIXME: Handle mana cost that can be paid with any color
            assert mana_color in player_mana_pool
            assert player_mana_pool[mana_color] >= mana_cost
            player_mana_pool[mana_color] -= mana_cost

        player_card_new_instance = player_card.create_new_instance(
            state=CardState(
                tapped=False,
                owner_player_id=self.player_index,
                started_turn_controlled_by_player_id=self.player_index,
            )
        )
        del player_hand[self.card_uuid]
        stack.append(player_card_new_instance)
        return game_state
