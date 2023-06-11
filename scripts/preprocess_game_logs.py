import os
import pickle
from pathlib import Path

import h5py
import numpy as np
from fire import Fire


def preprocess_game_logs(game_logs_folder_path: str, output_h5_path: str):
    Path(output_h5_path).parent.mkdir(parents=True, exist_ok=True)
    h5_file = h5py.File(output_h5_path, "w")
    action_general_dim = 16

    preprocessed_dataset_dict = {
        "game_state": {"global": [], "players": [], "zones": []},
        "action": {"general": [], "source_card_uuids": [], "target_card_uuids": []},
        "label": [],
    }

    file_paths = os.listdir(game_logs_folder_path)
    for n, file_name in enumerate(file_paths):
        file_path = os.path.join(game_logs_folder_path, file_name)
        print(f"Read game log from '{file_path}' ({n + 1} / {len(file_paths)})")
        with open(file_path, "rb") as f:
            data_dict = pickle.load(f)

        dataset = data_dict["dataset"]
        winner_player_index = data_dict["winner_player_index"]

        if len(dataset) > 2000:
            # FIXME: Lot of games have more than 150 000 steps
            continue

        for i, item_dict in enumerate(dataset):
            print(f"Process item {i + 1} / {len(dataset)}")

            game_state = item_dict["game_state"]
            action = item_dict["action"]

            game_state_vectors = game_state.to_vectors()
            if action is None:
                n_cards = len(game_state_vectors[0]["zones"])
                action_vectors = {
                    "general": np.zeros(action_general_dim),
                    "source_card_uuids": np.zeros(n_cards),
                    "target_card_uuids": np.zeros(n_cards),
                }
            else:
                action_vectors = action.to_vectors(game_state=game_state)

            label = -1
            if action is not None:
                # FIXME: Handle the case of action None properly (considering that it can be chosen by the winning player, thus affecting the label)
                if action.source_player_index is not None:
                    label = int(action.source_player_index == winner_player_index)

            for key, vector in game_state_vectors.items():
                preprocessed_dataset_dict["game_state"][key].append(vector)
            for key, vector in action_vectors.items():
                preprocessed_dataset_dict["action"][key].append(vector)
            preprocessed_dataset_dict["label"].append(label)

    for key, vector_list in preprocessed_dataset_dict["game_state"].items():
        preprocessed_dataset_dict["game_state"][key] = np.array(vector_list)
    for key, vector_list in preprocessed_dataset_dict["action"].items():
        preprocessed_dataset_dict["action"][key] = np.array(vector_list)
    preprocessed_dataset_dict["label"] = np.array(preprocessed_dataset_dict["label"])

    import pdb

    pdb.set_trace()


if __name__ == "__main__":
    Fire(preprocess_game_logs)
