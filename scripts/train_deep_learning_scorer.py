from pathlib import Path
from typing import Dict

import h5py
import mlflow
import numpy as np
import torch
import yaml
from fire import Fire
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint

from magic_the_gathering.players.deep_learning_based.models.v1 import DeepLearningScorerV1


class MTGDataset(torch.utils.data.Dataset):
    def __init__(self, h5_file, device, return_labels=True):
        self.h5_file = h5_file
        self.return_labels = return_labels
        self.device = device
        self.indices_with_a_label = np.where(self.h5_file["label"][:] != -1)[0]

    def __len__(self):
        return len(self.indices_with_a_label)

    def __getitem__(self, idx):
        idx = self.indices_with_a_label[idx]
        batch_game_state_vectors = {
            "global": torch.from_numpy(self.h5_file["game_state"]["global"][idx]).to(self.device),
            "players": torch.from_numpy(self.h5_file["game_state"]["players"][idx]).to(self.device),
            "zones": torch.from_numpy(self.h5_file["game_state"]["zones"][idx]).to(self.device),
            "zones_padding_mask": torch.from_numpy(self.h5_file["game_state"]["zones_padding_mask"][idx]).to(
                self.device
            ),
        }
        batch_action_vectors = {
            "general": torch.from_numpy(self.h5_file["action"]["general"][idx]).to(self.device),
            "source_card_uuids": torch.from_numpy(self.h5_file["action"]["source_card_uuids"][idx]).to(self.device),
            "source_card_uuids_padding_mask": torch.from_numpy(
                self.h5_file["action"]["source_card_uuids_padding_mask"][idx]
            ).to(self.device),
            "target_card_uuids": torch.from_numpy(self.h5_file["action"]["target_card_uuids"][idx]).to(self.device),
            "target_card_uuids_padding_mask": torch.from_numpy(
                self.h5_file["action"]["target_card_uuids_padding_mask"][idx]
            ).to(self.device),
        }
        if self.return_labels:
            batch_labels = torch.from_numpy(self.h5_file["label"][[idx]]).float().to(self.device)
            return batch_game_state_vectors, batch_action_vectors, batch_labels
        return batch_game_state_vectors, batch_action_vectors


def read_params(path: str) -> Dict:
    with open(path, "r") as f:
        params = yaml.safe_load(f)
    return params


def log_params_to_mlflow(params, prefix=None):
    if isinstance(params, dict):
        for key, value in params.items():
            log_params_to_mlflow(params=value, prefix=f"{prefix}.{key}" if prefix is not None else key)
    else:
        assert (
            params is None
            or isinstance(params, str)
            or isinstance(params, int)
            or isinstance(params, float)
            or isinstance(params, bool)
        ), f"Invalid params: {params}"
        mlflow.log_param(key=prefix, value=params)


def train_deep_learning_scorer(
    params_path: str,
    preprocessed_game_logs_path: str,
    model_folder_path: str,
    model_file_name: str,
):
    print(f"Load parameters from '{params_path}'")
    params = read_params(params_path)["deep_learning_scorer"]
    log_params_to_mlflow(params)
    mlflow.pytorch.autolog()

    print(f"Load preprocessed game logs from '{preprocessed_game_logs_path}'")
    h5_file = h5py.File(preprocessed_game_logs_path, "r")
    n_players = h5_file["game_state"]["players"].shape[1]
    player_dim = h5_file["game_state"]["players"].shape[-1]
    card_dim = h5_file["game_state"]["zones"].shape[-1]
    action_general_dim = h5_file["action"]["general"].shape[-1]

    print("Initialize model")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DeepLearningScorerV1(
        n_players=n_players,
        player_dim=player_dim,
        card_dim=card_dim,
        action_general_dim=action_general_dim,
        final_common_dim=params["hyper_parameters"]["final_common_dim"],
    ).to(device)

    print("Initialize data loaders")
    dataset = MTGDataset(h5_file=h5_file, return_labels=True, device=device)
    training_dataset, validation_dataset = torch.utils.data.random_split(
        dataset,
        lengths=[
            params["training"]["random_split"]["training_size"],
            params["training"]["random_split"]["validation_size"],
        ],
    )
    training_data_loader = torch.utils.data.DataLoader(
        training_dataset,
        batch_size=params["training"]["batch_size"],
        shuffle=True,
        drop_last=True,
        num_workers=0,
    )
    validation_data_loader = torch.utils.data.DataLoader(
        validation_dataset,
        batch_size=params["training"]["batch_size"],
        shuffle=False,
        drop_last=False,
        num_workers=0,
    )

    print("Initialize trainer")
    Path(model_folder_path).mkdir(parents=True, exist_ok=True)
    callbacks = [
        ModelCheckpoint(
            dirpath=model_folder_path,
            filename=model_file_name,
            **params["training"]["model_checkpoint"],
        ),
        EarlyStopping(
            **params["training"]["early_stopping"],
        ),
    ]
    trainer = Trainer(
        max_epochs=params["training"]["n_epochs"],
        devices="auto",
        deterministic=True,
        callbacks=callbacks,
    )

    print("Start training")
    trainer.fit(
        model=model,
        train_dataloaders=training_data_loader,
        val_dataloaders=validation_data_loader,
    )


if __name__ == "__main__":
    Fire(train_deep_learning_scorer)
