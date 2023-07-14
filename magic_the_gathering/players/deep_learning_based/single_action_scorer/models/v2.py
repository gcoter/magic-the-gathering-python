from typing import Dict, List

import torch
from pytorch_lightning import LightningModule

from magic_the_gathering.players.deep_learning_based.single_action_scorer.models.base import BaseSingleActionScorer


class SingleActionScorerV2(BaseSingleActionScorer):
    def __init__(
        self,
        game_state_global_dim: int,
        n_players: int,
        player_dim: int,
        max_n_zone_vectors: int,
        zone_vector_dim: int,
        action_general_dim: int,
        max_n_action_source_cards: int,
        max_n_action_target_cards: int,
        embedding_dim: int,
        transformer_n_layers: int,
        transformer_n_heads: int,
        transformer_dim_feedforward: int,
        dropout: float,
    ):
        super().__init__(
            max_n_zone_vectors=max_n_zone_vectors,
            zone_vector_dim=zone_vector_dim,
            max_n_action_source_cards=max_n_action_source_cards,
            max_n_action_target_cards=max_n_action_target_cards,
        )
        self.game_state_global_dim = game_state_global_dim
        self.n_players = n_players
        self.player_dim = player_dim
        self.action_general_dim = action_general_dim
        self.embedding_dim = embedding_dim
        self.transformer_n_layers = transformer_n_layers
        self.transformer_n_heads = transformer_n_heads
        self.transformer_dim_feedforward = transformer_dim_feedforward
        self.dropout = dropout

        # Modules
        self.action_processing_block = ActionProcessingBlock(
            action_general_dim=self.action_general_dim,
            max_n_action_source_cards=self.max_n_action_source_cards,
            max_n_action_target_cards=self.max_n_action_target_cards,
            zone_vector_dim=self.zone_vector_dim,
            output_dim=self.embedding_dim,
            transformer_n_layers=self.transformer_n_layers,
            transformer_n_heads=self.transformer_n_heads,
            transformer_dim_feedforward=self.transformer_dim_feedforward,
            dropout=self.dropout,
        )
        self.game_state_processing_block = GameStateProcessingBlock(
            game_state_global_dim=self.game_state_global_dim,
            n_players=self.n_players,
            player_dim=self.player_dim,
            max_n_zone_vectors=self.max_n_zone_vectors,
            zone_vector_dim=self.zone_vector_dim,
            output_dim=self.embedding_dim,
            transformer_n_layers=self.transformer_n_layers,
            transformer_n_heads=self.transformer_n_heads,
            transformer_dim_feedforward=self.transformer_dim_feedforward,
            dropout=self.dropout,
        )
        self.classification_block = ClassificationBlock(
            input_dim=self.embedding_dim,
        )

    def forward(
        self,
        batch_preprocessed_game_state_vectors: Dict[str, torch.Tensor],
        batch_preprocessed_action_vectors: Dict[str, torch.Tensor],
        batch_preprocessed_action_vectors_history: List[Dict[str, torch.Tensor]] = None,
    ):
        """
        Inputs:

        - batch_preprocessed_game_state_vectors:

        {
            "global": (batch_size, global_game_state_dim),
            "players": (batch_size, n_players, player_dim),
            "zones": (batch_size, max_n_zone_vectors, zone_vector_dim),
        }

        - batch_preprocessed_action_vectors:

        {
            "general": (batch_size, action_general_dim),
            "source_card_vectors": (batch_size, max_n_action_source_cards, zone_vector_dim)
            "target_card_vectors": (batch_size, max_n_action_target_cards, zone_vector_dim)
        }

        Outputs:
        - scores: (batch_size,)
        """
        batch_current_game_state_embedding = self.game_state_processing_block(batch_preprocessed_game_state_vectors)

        batch_action_embedding = self.action_processing_block(batch_preprocessed_action_vectors)

        batch_predicted_action_score = self.classification_block(
            batch_current_game_state_embedding, batch_action_embedding
        )

        return batch_predicted_action_score


class ActionProcessingBlock(LightningModule):
    def __init__(
        self,
        action_general_dim: int,
        max_n_action_source_cards: int,
        max_n_action_target_cards: int,
        zone_vector_dim: int,
        output_dim: int,
        transformer_n_layers: int = 1,
        transformer_n_heads: int = 1,
        transformer_dim_feedforward: int = 128,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.action_general_dim = action_general_dim
        self.max_n_action_source_cards = max_n_action_source_cards
        self.max_n_action_target_cards = max_n_action_target_cards
        self.zone_vector_dim = zone_vector_dim
        self.output_dim = output_dim
        self.transformer_n_layers = transformer_n_layers
        self.transformer_n_heads = transformer_n_heads
        self.transformer_dim_feedforward = transformer_dim_feedforward
        self.dropout = dropout

        # Modules
        self.general_mlp = torch.nn.Sequential(
            torch.nn.Linear(in_features=self.action_general_dim, out_features=self.output_dim), torch.nn.ReLU()
        )
        self.card_mlp = torch.nn.Sequential(
            torch.nn.Linear(in_features=self.zone_vector_dim, out_features=self.output_dim), torch.nn.ReLU()
        )
        self.type_embeddings = torch.nn.Embedding(num_embeddings=4, embedding_dim=self.output_dim)
        self.transformer_encoder = torch.nn.TransformerEncoder(
            encoder_layer=torch.nn.TransformerEncoderLayer(
                d_model=self.output_dim,
                nhead=self.transformer_n_heads,
                dim_feedforward=self.transformer_dim_feedforward,
                dropout=self.dropout,
                activation="relu",
                batch_first=True,
            ),
            num_layers=self.transformer_n_layers,
        )

    def forward(self, action_vectors: Dict[str, torch.Tensor]):
        """
        Inputs:
        - action_vectors:
        {
            general: (batch_size, action_general_dim)
            source_card_vectors: (batch_size, max_n_action_source_cards, zone_vector_dim)
            target_card_vectors: (batch_size, max_n_action_target_cards, zone_vector_dim)
        }

        Outputs:
        - action_embedding: (batch_size, output_dim)
        """
        action_general_embedding = self.__get_action_general_embedding(action_vectors["general"])
        action_source_card_embeddings = self.__get_action_source_card_embeddings(action_vectors["source_card_vectors"])
        action_target_card_embeddings = self.__get_action_target_card_embeddings(action_vectors["target_card_vectors"])

        action_embedding_for_prediction = self.__get_embedding_for_prediction(action_general_embedding)

        action_embeddings_sequence = torch.cat(
            [
                action_embedding_for_prediction[:, None],
                action_general_embedding[:, None],
                action_source_card_embeddings,
                action_target_card_embeddings,
            ],
            dim=1,
        )

        action_embeddings_sequence_after_transformer = self.transformer_encoder(action_embeddings_sequence)

        return action_embeddings_sequence_after_transformer[:, 0, :]

    def __get_embedding_for_prediction(self, action_general_embedding: torch.Tensor):
        batch_size = action_general_embedding.shape[0]
        idx = torch.zeros(batch_size).to(action_general_embedding).long()
        return self.type_embeddings(idx).to(action_general_embedding)

    def __get_action_general_embedding(self, action_general_vector: torch.Tensor) -> torch.Tensor:
        batch_size = action_general_vector.shape[0]
        action_general_embedding = self.general_mlp(action_general_vector)
        idx = 1 * torch.ones(batch_size).to(action_general_vector).long()
        action_general_embedding_type = self.type_embeddings(idx).to(action_general_vector)
        return action_general_embedding + action_general_embedding_type

    def __get_action_source_card_embeddings(self, action_source_card_vectors: torch.Tensor) -> torch.Tensor:
        batch_size = action_source_card_vectors.shape[0]
        action_source_card_embeddings = self.card_mlp(action_source_card_vectors)
        idx = 2 * torch.ones(batch_size, self.max_n_action_source_cards).to(action_source_card_vectors).long()
        action_source_card_embeddings_type = self.type_embeddings(idx).to(action_source_card_vectors)
        return action_source_card_embeddings + action_source_card_embeddings_type

    def __get_action_target_card_embeddings(self, action_target_card_vectors: torch.Tensor) -> torch.Tensor:
        batch_size = action_target_card_vectors.shape[0]
        action_target_card_embeddings = self.card_mlp(action_target_card_vectors)
        idx = 3 * torch.ones(batch_size, self.max_n_action_target_cards).to(action_target_card_vectors).long()
        action_target_card_embeddings_type = self.type_embeddings(idx).to(action_target_card_vectors)
        return action_target_card_embeddings + action_target_card_embeddings_type


class GameStateProcessingBlock(LightningModule):
    def __init__(
        self,
        game_state_global_dim: int,
        n_players: int,
        player_dim: int,
        max_n_zone_vectors: int,
        zone_vector_dim: int,
        output_dim: int,
        transformer_n_layers: int = 1,
        transformer_n_heads: int = 1,
        transformer_dim_feedforward: int = 128,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.game_state_global_dim = game_state_global_dim
        self.n_players = n_players
        self.player_dim = player_dim
        self.max_n_zone_vectors = max_n_zone_vectors
        self.zone_vector_dim = zone_vector_dim
        self.output_dim = output_dim
        self.transformer_n_layers = transformer_n_layers
        self.transformer_n_heads = transformer_n_heads
        self.transformer_dim_feedforward = transformer_dim_feedforward
        self.dropout = dropout

        # Modules
        self.global_mlp = torch.nn.Sequential(
            torch.nn.Linear(in_features=self.game_state_global_dim, out_features=self.output_dim), torch.nn.ReLU()
        )
        self.player_mlp = torch.nn.Sequential(
            torch.nn.Linear(in_features=self.player_dim, out_features=self.output_dim), torch.nn.ReLU()
        )
        self.zone_mlp = torch.nn.Sequential(
            torch.nn.Linear(in_features=self.zone_vector_dim, out_features=self.output_dim), torch.nn.ReLU()
        )
        self.type_embeddings = torch.nn.Embedding(num_embeddings=4, embedding_dim=self.output_dim)
        self.transformer_encoder = torch.nn.TransformerEncoder(
            encoder_layer=torch.nn.TransformerEncoderLayer(
                d_model=self.output_dim,
                nhead=self.transformer_n_heads,
                dim_feedforward=self.transformer_dim_feedforward,
                dropout=self.dropout,
                activation="relu",
                batch_first=True,
            ),
            num_layers=self.transformer_n_layers,
        )

    def forward(self, game_state_vectors: Dict[str, torch.Tensor]):
        """
        Inputs:
        - game_state_vectors:
        {
            global: (batch_size, game_state_global_dim)
            players: (batch_size, n_players, player_dim)
            zones: (batch_size, max_n_zone_vectors, zone_vector_dim)
        }

        Outputs:
        - game_state_embedding: (batch_size, output_dim)
        """
        global_embedding = self.__get_global_embedding(game_state_vectors["global"])
        player_embeddings = self.__get_player_embeddings(game_state_vectors["players"])
        zone_embeddings = self.__get_zone_embeddings(game_state_vectors["zones"])

        embedding_for_prediction = self.__get_embedding_for_prediction(global_embedding)

        embeddings_sequence = torch.cat(
            [embedding_for_prediction[:, None], global_embedding[:, None], player_embeddings, zone_embeddings], dim=1
        )

        embeddings_sequence_after_transformer = self.transformer_encoder(embeddings_sequence)

        return embeddings_sequence_after_transformer[:, 0, :]

    def __get_embedding_for_prediction(self, global_embedding: torch.Tensor):
        batch_size = global_embedding.shape[0]
        idx = torch.zeros(batch_size).to(global_embedding).long()
        return self.type_embeddings(idx).to(global_embedding)

    def __get_global_embedding(self, game_state_global_vector: torch.Tensor) -> torch.Tensor:
        batch_size = game_state_global_vector.shape[0]
        global_embedding = self.global_mlp(game_state_global_vector)
        idx = 1 * torch.ones(batch_size).to(global_embedding).long()
        global_embedding_type = self.type_embeddings(idx).to(global_embedding)
        return global_embedding + global_embedding_type

    def __get_player_embeddings(self, game_state_player_vectors: torch.Tensor) -> torch.Tensor:
        batch_size = game_state_player_vectors.shape[0]
        player_embeddings = self.player_mlp(game_state_player_vectors)
        idx = 2 * torch.ones(batch_size, self.n_players).to(player_embeddings).long()
        player_embeddings_type = self.type_embeddings(idx).to(player_embeddings)
        return player_embeddings + player_embeddings_type

    def __get_zone_embeddings(self, game_state_zone_vectors: torch.Tensor) -> torch.Tensor:
        batch_size = game_state_zone_vectors.shape[0]
        zone_embeddings = self.zone_mlp(game_state_zone_vectors)
        idx = 3 * torch.ones(batch_size, self.max_n_zone_vectors).to(zone_embeddings).long()
        zone_embeddings_type = self.type_embeddings(idx).to(zone_embeddings)
        return zone_embeddings + zone_embeddings_type


class ClassificationBlock(LightningModule):
    def __init__(self, input_dim: int):
        super().__init__()
        self.input_dim = input_dim

        # Modules
        self.mlp = torch.nn.Sequential(torch.nn.Linear(2 * self.input_dim, 1), torch.nn.Sigmoid())

    def forward(
        self, batch_current_game_state_embedding: torch.Tensor, batch_action_embedding: torch.Tensor
    ) -> torch.Tensor:
        """
        Inputs:
        - batch_current_game_state_embedding: (batch_size, input_dim)
        - batch_action_embedding: (batch_size, input_dim)

        Outputs:
        - batch_predicted_action_score: (batch_size,)
        """
        x = torch.cat([batch_current_game_state_embedding, batch_action_embedding], dim=1)
        return self.mlp(x)[:, 0]
