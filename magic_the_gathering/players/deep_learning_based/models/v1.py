import torch

from magic_the_gathering.players.deep_learning_based.models.base import BaseDeepLearningScorer


class DeepLearningScorerV1(BaseDeepLearningScorer):
    def __init__(
        self,
        n_players: int,
        player_dim: int,
        card_dim: int,
        action_general_dim: int,
        final_common_dim: int,
        transformer_n_layers: int,
        transformer_n_heads: int,
        dropout: float,
    ):
        super().__init__()
        self.n_players = n_players
        self.player_dim = player_dim
        self.card_dim = card_dim
        self.action_general_dim = action_general_dim
        self.final_common_dim = final_common_dim
        self.transformer_n_layers = transformer_n_layers
        self.transformer_n_heads = transformer_n_heads
        self.dropout = dropout

        # Define modules
        self.players_mlp = PlayersMLP(
            n_players=self.n_players, player_dim=self.player_dim, output_dim=self.final_common_dim
        )
        self.zones_transformer_encoder = ZonesTransformerEncoder(
            card_dim=self.card_dim,
            output_dim=self.final_common_dim,
            n_layers=self.transformer_n_layers,
            n_heads=self.transformer_n_heads,
            dropout=self.dropout,
        )
        self.action_general_mlp = ActionGeneralMLP(
            action_general_dim=self.action_general_dim, output_dim=self.final_common_dim
        )
        self.action_card_mlp = ActionCardMLP(card_dim=card_dim, output_dim=final_common_dim)
        self.action_transformer_encoder = ActionTransformerEncoder(
            input_dim=final_common_dim,
            n_layers=self.transformer_n_layers,
            n_heads=self.transformer_n_heads,
            dropout=self.dropout,
        )
        self.final_classification_mlp = FinalClassificationMLP(
            input_dim=3 * final_common_dim,
        )

    def forward(self, batch_game_state_vectors, batch_action_vectors):
        """
        batch_game_state_vectors:

        {
            "global": (batch_size, global_game_state_dim),
            "players": (batch_size, n_players, player_dim),
            "zones": (batch_size, n_cards, card_dim),
            "zones_padding_mask": (batch_size, n_cards)
        }

        batch_action_vectors:

        {
            "general": (batch_size, action_general_dim),
            "source_card_uuids": (batch_size, n_cards),
            "source_card_uuids_padding_mask": (batch_size, n_cards),
            "target_card_uuids": (batch_size, n_cards),
            "target_card_uuids_padding_mask": (batch_size, n_cards)
        }
        """
        batch_size = batch_game_state_vectors["global"].shape[0]

        # Compute players embedding
        # Shape: (batch_size, final_common_dim)
        players_embedding = self.players_mlp(batch_game_state_vectors["players"])

        # Compute zones embedding
        # Shape: (batch_size, final_common_dim)
        zones_embedding = self.zones_transformer_encoder(batch_game_state_vectors["zones"])

        # Compute actions embedding
        ## Compute general actions embedding first
        ## Shape: (batch_size, final_common_dim)
        action_general_embedding = self.action_general_mlp(batch_action_vectors["general"])

        ## Compute source cards embeddings
        ## Shape: (batch_size, n_source_cards, final_common_dim)
        selected_source_card_vectors = torch.nn.utils.rnn.pad_sequence(
            [
                batch_game_state_vectors["zones"][i][batch_action_vectors["source_card_uuids"][i]]
                for i in range(batch_size)
            ],
            batch_first=True,
        )
        action_source_card_embeddings = self.action_card_mlp(selected_source_card_vectors, is_source=True)

        ## Compute target cards embeddings
        ## Shape: (batch_size, n_target_cards, final_common_dim)
        selected_target_card_vectors = torch.nn.utils.rnn.pad_sequence(
            [
                batch_game_state_vectors["zones"][i][batch_action_vectors["target_card_uuids"][i]]
                for i in range(batch_size)
            ],
            batch_first=True,
        )
        action_target_card_embeddings = self.action_card_mlp(selected_target_card_vectors, is_source=False)

        ## Combine general, source and target embeddings
        ## Shape: (batch_size, 1 + n_source_cards + n_target_cards, final_common_dim)
        action_embeddings = torch.cat(
            [action_general_embedding.unsqueeze(1), action_source_card_embeddings, action_target_card_embeddings], dim=1
        )

        ## Compute actions embedding
        ## Shape: (batch_size, final_common_dim)
        action_embedding = self.action_transformer_encoder(action_embeddings)

        # Combine players, zones and actions embeddings
        # Shape: (batch_size, 3 * final_common_dim)
        final_embedding = torch.cat([players_embedding, zones_embedding, action_embedding], dim=1)

        # Compute final classification
        # Shape: (batch_size, 1)
        final_classification = self.final_classification_mlp(final_embedding)

        return final_classification


class PlayersMLP(torch.nn.Module):
    def __init__(self, n_players, player_dim, output_dim):
        super().__init__()
        self.n_players = n_players
        self.player_dim = player_dim
        self.output_dim = output_dim
        self.fc1 = torch.nn.Linear(n_players * player_dim, output_dim)
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        """
        x: (batch_size, n_players, player_dim)
        """
        batch_size = x.shape[0]
        x = x.view(batch_size, -1)
        x = self.fc1(x)
        x = self.relu(x)
        return x


class ZonesTransformerEncoder(torch.nn.Module):
    def __init__(self, card_dim, output_dim, n_heads=4, n_layers=2, dropout=0.1):
        super().__init__()
        self.card_dim = card_dim
        self.output_dim = output_dim
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.dropout = dropout
        self.initial_fc = torch.nn.Linear(self.card_dim, self.output_dim)
        self.relu = torch.nn.ReLU()
        self.transformer_encoder = torch.nn.TransformerEncoder(
            encoder_layer=torch.nn.TransformerEncoderLayer(
                d_model=self.output_dim,
                nhead=self.n_heads,
                dim_feedforward=self.output_dim,
                dropout=self.dropout,
                activation="relu",
                batch_first=True,
            ),
            num_layers=self.n_layers,
        )

    def forward(self, x):
        """
        x: (batch_size, n_cards, card_dim)
        """
        x = self.initial_fc(x)
        x = self.relu(x)
        x = self.transformer_encoder(x)
        return x[:, -1, :]


class ActionGeneralMLP(torch.nn.Module):
    def __init__(self, action_general_dim, output_dim):
        super().__init__()
        self.action_general_dim = action_general_dim
        self.output_dim = output_dim
        self.fc1 = torch.nn.Linear(self.action_general_dim, self.output_dim - 3)
        self.relu = torch.nn.ReLU()
        # Append the last 3 dimensions to mark it as an action
        # The 3 dimensions are:
        # - 1st: 1 if the vector corresponds to the general vector of an Action
        # - 2nd: 1 if the vector corresponds to a source card vector of the Action
        # - 3rd: 1 if the vector corresponds to a target card vector of the Action
        # As here we are only considering general actions, the 2nd and 3rd dimensions
        # are always 0
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.action_type = torch.nn.Parameter(torch.tensor([1.0, 0.0, 0.0])).to(self.device)

    def forward(self, x):
        """
        x: (batch_size, action_general_dim)
        """
        x = self.fc1(x)
        x = self.relu(x)
        x = torch.cat([x, self.action_type.unsqueeze(0).repeat(x.shape[0], 1)], dim=1)
        return x


class ActionCardMLP(torch.nn.Module):
    def __init__(self, card_dim, output_dim):
        super().__init__()
        self.card_dim = card_dim
        self.output_dim = output_dim
        self.fc1 = torch.nn.Linear(self.card_dim, self.output_dim - 3)
        self.relu = torch.nn.ReLU()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def forward(self, x, is_source=True):
        """
        x: (batch_size, n_cards, card_dim)
        """
        x = self.fc1(x)
        x = self.relu(x)

        # Append the last 3 dimensions to mark it as an action
        # The 3 dimensions are:
        # - 1st: 1 if the vector corresponds to the general vector of an Action
        # - 2nd: 1 if the vector corresponds to a source card vector of the Action
        # - 3rd: 1 if the vector corresponds to a target card vector of the Action
        # As here we are only considering card actions, the 1st dimension is always 0
        # and the 2nd and 3rd dimensions are 1 if the vector corresponds to a source
        # card and 0 if it corresponds to a target card
        if is_source:
            action_type = torch.tensor([[[0.0, 1.0, 0.0]]])
        else:
            action_type = torch.tensor([[[0.0, 0.0, 1.0]]])
        action_type = torch.nn.Parameter(action_type).repeat(x.shape[0], x.shape[1], 1).to(self.device)
        x = torch.cat([x, action_type], dim=2)
        return x


class ActionTransformerEncoder(torch.nn.Module):
    def __init__(self, input_dim, n_heads=4, n_layers=2, dropout=0.1):
        super().__init__()
        self.input_dim = input_dim
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.dropout = dropout
        self.transformer_encoder = torch.nn.TransformerEncoder(
            encoder_layer=torch.nn.TransformerEncoderLayer(
                d_model=self.input_dim,
                nhead=self.n_heads,
                dim_feedforward=self.input_dim,
                dropout=self.dropout,
                activation="relu",
                batch_first=True,
            ),
            num_layers=self.n_layers,
        )

    def forward(self, x):
        """
        x: (batch_size, sequence_length, input_dim)
        """
        x = self.transformer_encoder(x)
        return x[:, -1, :]


class FinalClassificationMLP(torch.nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.input_dim = input_dim
        self.fc1 = torch.nn.Linear(self.input_dim, 1)
        self.sigmoid = torch.nn.Sigmoid()

    def forward(self, x):
        """
        x: (batch_size, input_dim)
        """
        x = self.fc1(x)
        x = self.sigmoid(x)
        return x
