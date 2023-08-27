import random
from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.cards.state import CardState
from magic_the_gathering.game_state import GameState, ZonePosition


class CastCardAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_actions = []
        for player_index, player in enumerate(game_state.players):
            if player.is_alive:
                player_hand = game_state.zones[ZonePosition.HAND][player_index]
                for card_uuid, card in player_hand.items():
                    if card.can_be_cast_by_player(player=player):
                        possible_actions.append(
                            cls(
                                player_index=player_index,
                                card_uuid=card_uuid,
                            )
                        )
        return possible_actions

    def __init__(self, player_index: int, card_uuid: str):
        super().__init__(
            source_player_index=player_index,
            target_card_uuids=[card_uuid],
        )
        self.player_index = player_index
        self.card_uuid = card_uuid

    def _execute(self, game_state: GameState) -> GameState:
        player_hand = game_state.zones[ZonePosition.HAND][self.player_index]
        stack = game_state.zones[ZonePosition.STACK]

        assert self.card_uuid in player_hand.keys()
        player_card = player_hand[self.card_uuid]
        assert not player_card.is_land

        # Handle colored mana cost
        player_mana_pool = game_state.players[self.player_index].mana_pool
        for mana_color, mana_cost in player_card.mana_cost_dict.items():
            if mana_color != "any":
                assert mana_color in player_mana_pool
                assert player_mana_pool[mana_color] >= mana_cost
                player_mana_pool[mana_color] -= mana_cost

        # Handle generic mana cost
        for _ in range(player_card.mana_cost_dict["any"]):
            possible_colors = [mana_color for mana_color, mana_amount in player_mana_pool.items() if mana_amount > 0]
            chosen_color = random.choice(possible_colors)
            player_mana_pool[chosen_color] -= 1

        player_card_new_instance = player_card.create_new_instance(
            state=CardState(
                is_tapped=False,
                owner_player_id=self.player_index,
            )
        )
        del player_hand[self.card_uuid]
        stack[player_card_new_instance.uuid] = player_card_new_instance
        return game_state
