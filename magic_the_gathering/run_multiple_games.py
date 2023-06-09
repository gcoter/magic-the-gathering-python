from magic_the_gathering.run_one_game import run_one_game


def run_multiple_games(n_games: int = 100):
    for _ in range(n_games):
        run_one_game(n_players=2)


if __name__ == "__main__":
    run_multiple_games(n_games=10)
