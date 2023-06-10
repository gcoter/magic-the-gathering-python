from abc import abstractmethod

import torch
from pytorch_lightning import LightningModule


class BaseDeepLearningScorer(LightningModule):
    def __init__(self):
        super().__init__()
        self.loss = torch.nn.BCELoss()

    @abstractmethod
    def forward(self, batch_game_state_vectors, batch_action_vectors):
        """
        batch_game_state_vectors:

        {
            "global": (batch_size, global_game_state_dim),
            "players": (batch_size, n_players, player_dim),
            "zones": (batch_size, n_cards, card_dim),
        }

        batch_action_vectors:

        {
            "general": (batch_size, action_general_dim),
            "source_card_uuids": (batch_size, n_cards),
            "target_card_uuids": (batch_size, n_cards)
        }
        """
        raise NotImplementedError

    def __step(self, batch, batch_idx, base_metric_name):
        batch_game_state_vectors, batch_action_vectors, batch_target_scores = batch
        batch_predicted_scores = self.forward(
            batch_game_state_vectors=batch_game_state_vectors, batch_action_vectors=batch_action_vectors
        )
        batch_loss = self.loss(batch_predicted_scores, batch_target_scores)
        self.log(f"{base_metric_name}_loss", batch_loss, on_epoch=True)
        return batch_loss

    def training_step(self, batch, batch_idx):
        return self.__step(batch=batch, batch_idx=batch_idx, base_metric_name="training")

    def validation_step(self, batch, batch_idx):
        return self.__step(batch=batch, batch_idx=batch_idx, base_metric_name="validation")

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        batch_game_state_vectors, batch_action_vectors = batch
        batch_predicted_scores = self.forward(
            batch_game_state_vectors=batch_game_state_vectors, batch_action_vectors=batch_action_vectors
        )
        return batch_predicted_scores

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters())

    def get_n_parameters(self):
        return sum(p.numel() for p in self.parameters())
