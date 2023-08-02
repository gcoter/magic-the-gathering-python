from typing import Dict, List, Optional
from uuid import uuid4

import numpy as np
import pandas as pd

from magic_the_gathering.cards.state import CardState
from magic_the_gathering.players.base import Player


class Card:
    @classmethod
    def from_series(cls, series: pd.Series):
        color_identity = series["color_identity"]
        if isinstance(color_identity, str):
            color_identity = (
                color_identity.replace('"', "").replace("'", "").replace("[", "").replace("]", "").strip().split(", ")
            )
        assert isinstance(color_identity, list)
        return cls(
            scryfall_uuid=series["id"],
            name=series["name"],
            color_identity=color_identity,
            type=series["type_line"],
            text=series["oracle_text"] if not pd.isna(series["oracle_text"]) else "",
            mana_cost=series["mana_cost"],  # FIXME: did not look for consequences of this addition
            mana_cost_dict=Card.convert_mana_cost_to_dict(series["mana_cost"])
            if not pd.isna(series["mana_cost"])
            else None,
            power=series["power"] if not pd.isna(series["power"]) else "",
            toughness=series["toughness"] if not pd.isna(series["toughness"]) else "",
        )

    @staticmethod
    def convert_mana_cost_to_dict(mana_cost) -> Dict[str, int]:
        mana_cost_list = mana_cost.replace("{", "").replace("}", " ").strip().split(" ")
        mana_cost_dict = {
            "W": mana_cost_list.count("W"),
            "U": mana_cost_list.count("U"),
            "B": mana_cost_list.count("B"),
            "R": mana_cost_list.count("R"),
            "G": mana_cost_list.count("G"),
        }
        try:
            mana_cost_dict["any"] = int(mana_cost_list[0])
        except ValueError:
            mana_cost_dict["any"] = 0
        return mana_cost_dict

    def __init__(
        self,
        scryfall_uuid: str,
        name: str,
        color_identity: List[str],
        type: str,
        text: str,
        mana_cost: str,
        mana_cost_dict: Optional[Dict[str, int]] = None,
        power: Optional[str] = "",
        toughness: Optional[str] = "",
        state: Optional[CardState] = None,
    ):
        self.uuid = str(uuid4())
        self.scryfall_uuid = scryfall_uuid
        self.name = name
        self.color_identity = color_identity
        self.type = type
        self.text = text
        self.mana_cost = mana_cost
        self.mana_cost_dict = mana_cost_dict
        self.power = power
        self.toughness = toughness
        self.state = state

    def create_new_instance(self, state: Optional[CardState] = None):
        return Card(
            scryfall_uuid=self.scryfall_uuid,
            name=self.name,
            color_identity=self.color_identity,
            type=self.type,
            text=self.text,
            mana_cost_dict=self.mana_cost_dict,
            power=self.power,
            toughness=self.toughness,
            state=state,
        )

    def get_power(self) -> int:
        if self.power == "*" or self.power == "":
            return 0
        return int(self.power)

    def get_toughness(self) -> int:
        if self.toughness == "*" or self.toughness == "":
            return 0
        return int(self.toughness)

    def can_be_cast_by_player(self, player: Player) -> bool:
        if self.is_land:
            return False
        if self.mana_cost_dict is None:
            return False
        for mana_color, mana_cost in self.mana_cost_dict.items():
            if mana_color != "any":
                if mana_color not in player.mana_pool:
                    return False
                if player.mana_pool[mana_color] < mana_cost:
                    return False
        player_pool_value = sum(player.mana_pool.values())
        mana_value = sum(self.mana_cost_dict.values())
        if player_pool_value < mana_value:
            return False
        return True

    @property
    def main_type(self) -> str:
        return self.type.split("—")[0].strip()

    @property
    def subtypes(self) -> str:
        return self.type.split("—")[1].strip()

    @property
    def is_non_permanent(self) -> bool:
        return self.is_instant or self.is_sorcery

    @property
    def is_permanent(self) -> bool:
        return not self.is_non_permanent

    @property
    def is_land(self) -> bool:
        return "land" in self.type.lower()

    @property
    def is_creature(self) -> bool:
        return "creature" in self.type.lower()

    @property
    def is_instant(self) -> bool:
        return "instant" in self.type.lower()

    @property
    def is_sorcery(self) -> bool:
        return "sorcery" in self.type.lower()

    @property
    def is_enchantment(self) -> bool:
        return "enchantment" in self.type.lower()

    @property
    def is_artifact(self) -> bool:
        return "artifact" in self.type.lower()

    @property
    def is_planeswalker(self) -> bool:
        return "planeswalker" in self.type.lower()

    @property
    def main_color(self) -> str:
        # FIXME: Handle multi-color cards
        return self.color_identity[0]

    def __repr__(self) -> str:
        return f"Card(uuid={self.uuid}, name={self.name}, color_identity={self.color_identity}, type={self.type}, mana_cost={self.mana_cost_dict}, power={self.get_power()}, toughness={self.get_toughness()}, state={self.state})"

    def __str__(self) -> str:
        return self.__repr__()

    def to_json_dict(self) -> Dict:
        return {
            "uuid": self.uuid,
            "scryfall_uuid": self.scryfall_uuid,
            "name": self.name,
            "color_identity": self.color_identity,
            "type": self.type,
            "text": self.text,
            "mana_cost_dict": self.mana_cost_dict,
            "power": self.power,
            "toughness": self.toughness,
            "state": self.state.to_json_dict() if self.state is not None else None,
        }

    def to_vector(self) -> np.ndarray:
        color_identity_vector = self.__color_identity_to_vector()
        type_vector = self.__type_to_vector()
        power_toughness_vector = self.__power_toughness_to_vector()
        mana_cost_vector = self.__mana_cost_to_vector()
        state_vector = self.state.to_vector() if self.state is not None else np.zeros(2)
        return np.concatenate(
            [
                color_identity_vector,
                type_vector,
                power_toughness_vector,
                mana_cost_vector,
                state_vector,
            ]
        )

    def __color_identity_to_vector(self) -> np.ndarray:
        color_identity_vector = np.zeros(5)
        for index, color in enumerate(["W", "U", "B", "R", "G"]):
            if color in self.color_identity:
                color_identity_vector[index] = 1
        return color_identity_vector

    def __mana_cost_to_vector(self) -> np.ndarray:
        mana_cost_vector = np.zeros(6)
        if self.mana_cost_dict is None:
            return mana_cost_vector
        for index, color in enumerate(["W", "U", "B", "R", "G"]):
            mana_cost_vector[index] = self.mana_cost_dict.get(color, 0)
        mana_cost_vector[5] = self.mana_cost_dict.get("any", 0)
        return mana_cost_vector

    def __type_to_vector(self) -> np.ndarray:
        return np.array(
            [
                self.is_land,
                self.is_creature,
                self.is_instant,
                self.is_sorcery,
                self.is_enchantment,
                self.is_artifact,
                self.is_planeswalker,
            ]
        )

    def __power_toughness_to_vector(self) -> np.ndarray:
        return np.array([self.get_power(), self.get_toughness()])
