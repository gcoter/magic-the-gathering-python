from magic_the_gathering.game_modes.base import GameMode


class CommanderGameMode(GameMode):
    def __init__(self):
        super().__init__(
            name="Commander Game Mode",
            initial_life_points=20,
            initial_hand_size=7,
        )
