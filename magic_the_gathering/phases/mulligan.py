import numpy as np

from magic_the_gathering.actions.draw import DrawAction
from magic_the_gathering.actions.move_all_from_hand_to_library import MoveAllFromHandToLibraryAction
from magic_the_gathering.actions.none import NoneAction
from magic_the_gathering.actions.put_card_to_bottom_of_library import PutCardToBottomOfLibraryAction
from magic_the_gathering.actions.shuffle import ShuffleAction
from magic_the_gathering.actions.take_mulligan import TakeMulliganAction
from magic_the_gathering.game_state import GameState, ZonePosition
from magic_the_gathering.phases.base import Phase


class MulliganPhase(Phase):
    def __init__(self):
        super().__init__(
            name="Mulligan Phase",
        )

    def _run(self, game_state: GameState) -> GameState:
        take_mulligan_by_player = np.array([False for _ in range(game_state.n_players)])
        n_mulligans_taken_by_player = np.array([0 for _ in range(game_state.n_players)])
        while True:
            for player_index, player in enumerate(game_state.players):
                self.logger.debug(f"----- Player {player_index} -----")
                player_hand = game_state.zones[ZonePosition.HAND][player_index]

                if len(player_hand) == 0:
                    # Draw initial_hand_size cards
                    for _ in range(game_state.game_mode.initial_hand_size):
                        game_state = DrawAction(player_index=player_index).execute(game_state=game_state)

                    # Put n_mulligans cards on the bottom of the library
                    for _ in range(n_mulligans_taken_by_player[player_index]):
                        possible_actions = [
                            action
                            for action in PutCardToBottomOfLibraryAction.list_possible_actions(game_state=game_state)
                            if action.source_zone == ZonePosition.HAND and action.target_player_index == player_index
                        ]
                        action = player.choose_action(
                            game_state=game_state,
                            possible_actions=possible_actions,
                        )
                        game_state = action.execute(game_state)

                    # Choose whether to take a mulligan (if it is still possible)
                    possible_actions = [NoneAction()]
                    if n_mulligans_taken_by_player[player_index] < game_state.game_mode.initial_hand_size:
                        possible_actions.append(TakeMulliganAction(source_player_index=player_index))
                    action = player.choose_action(
                        game_state=game_state,
                        possible_actions=possible_actions,
                    )
                    game_state = action.execute(game_state)
                    if isinstance(action, TakeMulliganAction):
                        take_mulligan_by_player[player_index] = True
                        n_mulligans_taken_by_player[player_index] += 1

                        # Move all cards from hand to library
                        game_state = MoveAllFromHandToLibraryAction(target_player_index=player_index).execute(
                            game_state
                        )

                        # Shuffle library
                        game_state = ShuffleAction(zone=ZonePosition.LIBRARY, player_index=player_index).execute(
                            game_state
                        )
                    else:
                        take_mulligan_by_player[player_index] = False

            if ~np.any(take_mulligan_by_player):
                break

        return game_state
