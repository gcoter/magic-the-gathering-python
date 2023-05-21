from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_state import GameState, ZonePosition


class DrawAction(Action):
    def __init__(
        self,
        owner: str,
        player_index: int,
        n_cards: int = 1,
    ):
        super().__init__(owner=owner)
        self.player_index = player_index
        self.n_cards = n_cards

    def execute(self, game_state: GameState) -> GameState:
        player_library = game_state.zones[ZonePosition.LIBRARY][self.player_index]
        player_hand = game_state.zones[ZonePosition.HAND][self.player_index]
        n_cards = min(n_cards, len(player_library))
        drawn_cards = [player_library.pop(0) for _ in range(self.n_cards)]
        for drawn_card in drawn_cards:
            player_hand[drawn_card.uuid] = drawn_card
        return game_state
