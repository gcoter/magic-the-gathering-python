from typing import Dict, List

import numpy as np
import pandas as pd


class GameLogsDataset:
    def __init__(self):
        self.__data = {}

    def get_all(self) -> Dict:
        return self.__data

    def list_game_ids(self) -> List[str]:
        return list(self.__data.keys())

    def get_one_game(self, game_id: str) -> Dict:
        assert game_id in self.__data
        return self.__data[game_id]

    def get_one_game_items(self, game_id: str) -> List[Dict]:
        assert game_id in self.__data
        return self.__data[game_id]["items"]

    def get_item(self, game_id: str, item_index: int) -> Dict:
        assert game_id in self.__data
        items = self.__data[game_id]["items"]
        assert 0 <= item_index < len(items)
        return items[item_index]

    def get_action_history(
        self,
        game_id: str,
    ) -> List[Dict[str, np.ndarray]]:
        assert game_id in self.__data
        return self.__data[game_id]["action_history"]

    def get_winner_player_index(self, game_id: str) -> int:
        assert game_id in self.__data
        return self.__data[game_id]["winner_player_index"]

    def get_max_zones_length(self):
        return max(
            [
                len(item_dict["game_state"]["zones"])
                for game_id in self.list_game_ids()
                for item_dict in self.get_one_game_items(game_id=game_id)
            ]
        )

    def add(
        self,
        game_id: str,
        player_index: int,
        action_history_index: int,
        game_state: Dict[str, np.ndarray],
        possible_actions: List[Dict[str, np.ndarray]],
        chosen_action_index: int,
    ):
        self.__register_game_id_if_not_exist(game_id=game_id)
        if "items" not in self.__data[game_id]:
            self.__data[game_id]["items"] = []
        self.__data[game_id]["items"].append(
            {
                "player_index": player_index,
                "action_history_index": action_history_index,
                "game_state": game_state,
                "possible_actions": possible_actions,
                "chosen_action_index": chosen_action_index,
            }
        )

    def set_action_history(self, game_id: str, action_history: List[Dict[str, np.ndarray]]):
        self.__register_game_id_if_not_exist(game_id=game_id)
        self.__data[game_id]["action_history"] = action_history

    def set_winner_player_index(self, game_id: str, winner_player_index: int):
        self.__register_game_id_if_not_exist(game_id=game_id)
        self.__data[game_id]["winner_player_index"] = winner_player_index

    def __register_game_id_if_not_exist(self, game_id: str):
        if game_id not in self.__data:
            self.__data[game_id] = {}

    def get_index(self) -> pd.DataFrame:
        index_df = []
        for game_id in self.list_game_ids():
            items = self.get_one_game_items(game_id=game_id)
            for item_index in range(len(items)):
                index_df.append({"game_id": game_id, "item_index": item_index})
        index_df = pd.DataFrame(index_df)
        return index_df

    def get_n_players(self) -> int:
        game_id = self.list_game_ids()[0]
        return len(self.__data[game_id]["items"][0]["game_state"]["players"])

    def get_player_dim(self) -> int:
        game_id = self.list_game_ids()[0]
        return self.__data[game_id]["items"][0]["game_state"]["players"].shape[1]

    def get_zone_vector_dim(self) -> int:
        game_id = self.list_game_ids()[0]
        return self.__data[game_id]["items"][0]["game_state"]["zones"].shape[1]

    def get_action_general_dim(self) -> int:
        game_id = self.list_game_ids()[0]
        return len(self.__data[game_id]["items"][0]["possible_actions"][0]["general"])
