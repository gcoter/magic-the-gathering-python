import json
import pickle
from pathlib import Path

import numpy as np
from fire import Fire

from magic_the_gathering.actions.base import Action
from magic_the_gathering.game_logs_dataset import GameLogsDataset


def compute_game_logs_stats(game_logs_dataset_path: str, metrics_json_path: str = None):
    print(f"Load game logs dataset from '{game_logs_dataset_path}'")
    with open(game_logs_dataset_path, "rb") as f:
        game_logs_dataset: GameLogsDataset = pickle.load(f)

    print("Compute stats")
    n_instances_per_player = {}
    n_instances_per_action_type = {}
    n_instances_per_player_per_action_type = {}
    n_total_instances = 0
    n_winning_instances = 0
    for game_id in game_logs_dataset.list_game_ids():
        items = game_logs_dataset.get_one_game_items(game_id=game_id)
        winner_player_index = game_logs_dataset.get_winner_player_index(game_id=game_id)
        for item_index in range(len(items)):
            item_dict = items[item_index]
            chosen_action_index = item_dict["chosen_action_index"]
            chosen_action_vectors = item_dict["possible_actions"][chosen_action_index]
            action_type_one_hot_vector = chosen_action_vectors["general"][: len(Action.TYPES)]
            action_type_index = int(np.argmax(action_type_one_hot_vector))
            action_type = Action.TYPES[action_type_index]
            source_player_index = chosen_action_vectors["source_player_index"]

            n_total_instances += 1

            if source_player_index == winner_player_index:
                n_winning_instances += 1

            if source_player_index not in n_instances_per_player:
                n_instances_per_player[source_player_index] = 0
            n_instances_per_player[source_player_index] += 1

            if action_type not in n_instances_per_action_type:
                n_instances_per_action_type[action_type] = 0
            n_instances_per_action_type[action_type] += 1

            if source_player_index not in n_instances_per_player_per_action_type:
                n_instances_per_player_per_action_type[source_player_index] = {}
            if action_type not in n_instances_per_player_per_action_type[source_player_index]:
                n_instances_per_player_per_action_type[source_player_index][action_type] = 0
            n_instances_per_player_per_action_type[source_player_index][action_type] += 1

    metrics_dict = {
        "n_instances_per_player_per_action_type": n_instances_per_player_per_action_type,
        "n_instances_per_player": n_instances_per_player,
        "n_instances_per_action_type": n_instances_per_action_type,
        "n_total_instances": n_total_instances,
        "n_winning_instances": n_winning_instances,
        "winning_proportion": round(n_winning_instances / n_total_instances, 3),
    }

    if metrics_json_path is not None:
        print(f"Save stats to '{metrics_json_path}'")
        Path(metrics_json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(metrics_json_path, "w") as f:
            json.dump(metrics_dict, f, indent=4)


if __name__ == "__main__":
    Fire(compute_game_logs_stats)
