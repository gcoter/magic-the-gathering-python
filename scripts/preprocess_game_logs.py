import os
import pickle
from pathlib import Path

import h5py
import numpy as np
from fire import Fire


def preprocess_game_logs(game_logs_folder_path: str, output_h5_path: str):
    Path(output_h5_path).parent.mkdir(parents=True, exist_ok=True)

    preprocessed_dataset_dict = {
        "game_id": [],
        "game_state": {"global": [], "players": [], "zones": [], "zones_padding_mask": []},
        "action": {
            "general": [],
            "source_card_uuids": [],
            "source_card_uuids_padding_mask": [],
            "target_card_uuids": [],
            "target_card_uuids_padding_mask": [],
        },
        "label": [],
    }

    file_paths = os.listdir(game_logs_folder_path)
    for n, file_name in enumerate(file_paths[:2]):
        file_path = os.path.join(game_logs_folder_path, file_name)
        print(f"Read game log from '{file_path}' ({n + 1} / {len(file_paths)})")
        with open(file_path, "rb") as f:
            data_dict = pickle.load(f)

        dataset = data_dict["dataset"]
        winner_player_index = data_dict["winner_player_index"]

        for i, item_dict in enumerate(dataset):
            # if (i + 1) % 1000 == 0:
            #     print(f"Process item {i + 1} / {len(dataset)}")

            game_state_vectors = item_dict["game_state"]
            game_id = game_state_vectors["game_id"]
            action_vectors = item_dict["action"]
            source_player_index = action_vectors["source_player_index"]

            label = -1
            # FIXME: Handle the case of action None properly (considering that it can be chosen by the winning player, thus affecting the label)
            if source_player_index is not None:
                label = int(source_player_index == winner_player_index)

            preprocessed_dataset_dict["game_id"].append(game_id)
            for key, vector in game_state_vectors.items():
                if key != "game_id":
                    preprocessed_dataset_dict["game_state"][key].append(vector)
            for key, vector in action_vectors.items():
                if key != "source_player_index":
                    preprocessed_dataset_dict["action"][key].append(vector)
            preprocessed_dataset_dict["label"].append(label)

    preprocessed_dataset_dict["game_id"] = np.array(preprocessed_dataset_dict["game_id"], dtype="S")

    preprocessed_dataset_dict["game_state"]["global"] = np.array(preprocessed_dataset_dict["game_state"]["global"])
    preprocessed_dataset_dict["game_state"]["players"] = np.array(preprocessed_dataset_dict["game_state"]["players"])

    max_n_cards = max([len(zones) for zones in preprocessed_dataset_dict["game_state"]["zones"]])
    vector_dim = preprocessed_dataset_dict["game_state"]["zones"][-1].shape[1]
    for i, vector in enumerate(preprocessed_dataset_dict["game_state"]["zones"]):
        pad_width = ((0, max_n_cards - len(vector)), (0, 0))
        if len(vector.shape) == 1:
            vector = np.expand_dims(vector, axis=0)
            pad_width = ((0, max_n_cards - len(vector)), (0, vector_dim - vector.shape[1]))
        padding_mask = np.zeros(max_n_cards)
        if len(vector) > 0 and vector.shape[1] > 0:
            padding_mask[: len(vector)] = 1
        preprocessed_dataset_dict["game_state"]["zones"][i] = np.pad(vector, pad_width)
        preprocessed_dataset_dict["game_state"]["zones_padding_mask"].append(padding_mask)
    preprocessed_dataset_dict["game_state"]["zones"] = np.array(preprocessed_dataset_dict["game_state"]["zones"])
    preprocessed_dataset_dict["game_state"]["zones_padding_mask"] = np.array(
        preprocessed_dataset_dict["game_state"]["zones_padding_mask"]
    )

    preprocessed_dataset_dict["action"]["general"] = np.array(preprocessed_dataset_dict["action"]["general"])

    for i, vector in enumerate(preprocessed_dataset_dict["action"]["source_card_uuids"]):
        pad_width = (0, max_n_cards - len(vector))
        padding_mask = np.zeros((max_n_cards, vector_dim))
        padding_mask[: len(vector)] = 1
        preprocessed_dataset_dict["action"]["source_card_uuids"][i] = np.pad(vector, pad_width)
        preprocessed_dataset_dict["action"]["source_card_uuids_padding_mask"].append(padding_mask)
    for i, vector in enumerate(preprocessed_dataset_dict["action"]["target_card_uuids"]):
        pad_width = (0, max_n_cards - len(vector))
        padding_mask[: len(vector)] = 1
        preprocessed_dataset_dict["action"]["target_card_uuids"][i] = np.pad(vector, pad_width)
        preprocessed_dataset_dict["action"]["target_card_uuids_padding_mask"].append(padding_mask)
    preprocessed_dataset_dict["action"]["source_card_uuids"] = np.array(
        preprocessed_dataset_dict["action"]["source_card_uuids"]
    )
    preprocessed_dataset_dict["action"]["source_card_uuids_padding_mask"] = np.array(
        preprocessed_dataset_dict["action"]["source_card_uuids_padding_mask"]
    )
    preprocessed_dataset_dict["action"]["target_card_uuids"] = np.array(
        preprocessed_dataset_dict["action"]["target_card_uuids"]
    )
    preprocessed_dataset_dict["action"]["target_card_uuids_padding_mask"] = np.array(
        preprocessed_dataset_dict["action"]["target_card_uuids_padding_mask"]
    )

    preprocessed_dataset_dict["label"] = np.array(preprocessed_dataset_dict["label"])

    # Print shapes
    print("\n===== Shapes =====")
    print(f"game_id: {preprocessed_dataset_dict['game_id'].shape}")
    for key, vector in preprocessed_dataset_dict["game_state"].items():
        print(f"game_state/{key}: {vector.shape}")
    for key, vector in preprocessed_dataset_dict["action"].items():
        print(f"action/{key}: {vector.shape}")
    print(f"label: {preprocessed_dataset_dict['label'].shape}\n")

    # Save to h5
    print(f"Save preprocessed dataset to '{output_h5_path}'")
    h5_file = h5py.File(output_h5_path, "w")
    h5_file.create_dataset("game_id", data=preprocessed_dataset_dict["game_id"])
    for key, vector in preprocessed_dataset_dict["game_state"].items():
        h5_file.create_dataset(f"game_state/{key}", data=vector)
    for key, vector in preprocessed_dataset_dict["action"].items():
        h5_file.create_dataset(f"action/{key}", data=vector)
    h5_file.create_dataset("label", data=preprocessed_dataset_dict["label"])


if __name__ == "__main__":
    Fire(preprocess_game_logs)
