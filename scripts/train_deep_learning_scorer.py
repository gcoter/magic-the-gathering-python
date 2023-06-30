import pickle
from pathlib import Path
from typing import Dict

import mlflow
import torch
import yaml
from fire import Fire
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint

from magic_the_gathering.game_logs_dataset import GameLogsDataset
from magic_the_gathering.players.deep_learning_based.single_action_scorer.dataset import SingleActionScorerDataset
from magic_the_gathering.players.deep_learning_based.single_action_scorer.models.v1 import SingleActionScorerV1
from magic_the_gathering.utils import set_random_seed


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
    game_logs_dataset_path: str,
    model_folder_path: str,
    model_file_name: str,
):
    print(f"Load parameters from '{params_path}'")
    params = read_params(params_path)["deep_learning_scorer"]
    log_params_to_mlflow(params)
    mlflow.pytorch.autolog()

    set_random_seed(seed=42)
    generator = torch.Generator().manual_seed(42)

    print(f"Load game logs dataset from '{game_logs_dataset_path}'")
    with open(game_logs_dataset_path, "rb") as f:
        game_logs_dataset: GameLogsDataset = pickle.load(f)

    n_players = game_logs_dataset.get_n_players()
    player_dim = game_logs_dataset.get_player_dim()
    card_dim = game_logs_dataset.get_zone_dim()
    action_general_dim = game_logs_dataset.get_action_general_dim()

    assert params["hyper_parameters"]["n_players"] == n_players
    assert params["hyper_parameters"]["player_dim"] == player_dim
    assert params["hyper_parameters"]["card_dim"] == card_dim
    assert params["hyper_parameters"]["action_general_dim"] == action_general_dim

    print("Initialize model")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SingleActionScorerV1(
        **params["hyper_parameters"],
    ).to(device)

    print("Initialize data loaders")
    dataset = SingleActionScorerDataset(
        game_logs_dataset=game_logs_dataset,
        max_n_cards=params["hyper_parameters"]["max_n_cards"],
        device=device,
        return_label=True,
    )
    training_dataset, validation_dataset = torch.utils.data.random_split(
        dataset,
        lengths=[
            params["training"]["random_split"]["training_size"],
            params["training"]["random_split"]["validation_size"],
        ],
        generator=generator,
    )
    training_data_loader = torch.utils.data.DataLoader(
        training_dataset,
        batch_size=params["training"]["batch_size"],
        shuffle=True,
        drop_last=True,
        num_workers=0,
        generator=generator,
    )
    validation_data_loader = torch.utils.data.DataLoader(
        validation_dataset,
        batch_size=params["training"]["batch_size"],
        shuffle=False,
        drop_last=False,
        num_workers=0,
        generator=generator,
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
