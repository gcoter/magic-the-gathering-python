import numpy as np

from magic_the_gathering.game_state import GameState
from magic_the_gathering.phases.base import Phase


class MulliganPhase(Phase):
    def __init__(self):
        # TODO: Is players_get_priority relevant here?
        super().__init__(
            name="Mulligan Phase",
        )

    def _run(self, game_state: GameState) -> GameState:
        take_mulligan_by_player = np.array([False for _ in range(self.players)])
        # TODO: game_state.game_mode.initial_hand_size is ugly, should we assume the hand are already initialized elsewhere (in GameState)?
        n_cards_to_draw_by_player = np.array(
            [game_state.game_mode.initial_hand_size for _ in range(game_state.players)]
        )
        while True:
            for index, player in enumerate(self.players):
                # Each player draws as many cards as necessary to create their hand
                # TODO: if I understood the code well, this isn't the latest mulligan rule: the London mulligan says that you always draw 7 cards, then put n on the bottom of the library when you keep, when n is the number of times you mulliganed
                if len(game_state.hands[index]) == 0:
                    game_state.draw_cards_from_deck(player_index=index, n_cards=n_cards_to_draw_by_player[index])

                if take_mulligan_by_player[index]:
                    self.__logger.info(f"Player '{index}' takes a mulligan")
                    game_state.add_all_hand_cards_to_deck(player_index=index)
                    game_state.shuffle_deck(player_index=index)
                    game_state.draw_cards_from_deck(player_index=index, n_cards=n_cards_to_draw_by_player[index])

                # Each player decides whether they want to take a mulligan
                take_mulligan_by_player[index] = player.choose_mulligan(game_state=game_state)
                if take_mulligan_by_player[index]:
                    n_cards_to_draw_by_player[index] -= 1

                # If a mulligan would cause a player to draw no card, then forbid it
                if n_cards_to_draw_by_player[index] <= 0:
                    take_mulligan_by_player[index] = False

            if ~np.any(take_mulligan_by_player):
                break

        return game_state
