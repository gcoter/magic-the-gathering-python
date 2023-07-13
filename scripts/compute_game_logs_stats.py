import json
import pickle
from pathlib import Path

from fire import Fire

from magic_the_gathering.game_logs_dataset import GameLogsDataset


def compute_game_logs_stats(game_logs_dataset_path: str, metrics_json_path: str = None):
    print(f"Load game logs dataset from '{game_logs_dataset_path}'")
    with open(game_logs_dataset_path, "rb") as f:
        game_logs_dataset: GameLogsDataset = pickle.load(f)

    print("Compute stats")
    metrics_dict = game_logs_dataset.compute_stats()

    if metrics_json_path is not None:
        print(f"Save stats to '{metrics_json_path}'")
        Path(metrics_json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(metrics_json_path, "w") as f:
            json.dump(metrics_dict, f, indent=4)


if __name__ == "__main__":
    Fire(compute_game_logs_stats)
