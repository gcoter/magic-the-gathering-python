class GameOverException(Exception):
    def __init__(self, winner_player_index):
        self.winner_player_index = winner_player_index

    def __str__(self):
        return "Game Over. Winner: Player {}".format(self.winner_player_index)
