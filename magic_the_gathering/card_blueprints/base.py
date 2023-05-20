from abc import abstractmethod
from typing import Dict, Optional

import pandas as pd

from magic_the_gathering.card_objects.base import CardObject
from magic_the_gathering.card_objects.state import CardObjectState


class CardBlueprint:
    @staticmethod
    def convert_mana_cost_to_dict(mana_cost) -> Dict[str, int]:
        mana_cost_list = mana_cost.replace("{", "").replace("}", " ").strip().split(" ")
        mana_cost_dict = {
            "white": mana_cost_list.count("W"),
            "blue": mana_cost_list.count("U"),
            "black": mana_cost_list.count("B"),
            "red": mana_cost_list.count("R"),
            "green": mana_cost_list.count("G"),
        }
        try:
            mana_cost_dict["any"] = int(mana_cost_list[0])
        except ValueError:
            mana_cost_dict["any"] = 0
        return mana_cost_dict

    def __init__(
        self,
        uuid: str,
        name: str,
        type: str,
        text: str,
        mana_cost_dict: Optional[Dict[str, int]] = None,
    ):
        self.uuid = uuid
        self.name = name
        self.type = type
        self.text = text
        self.mana_cost_dict = mana_cost_dict

    @classmethod
    def from_series(cls, series: pd.Series):
        return cls(
            uuid=series["id"],
            name=series["name"],
            type=series["type_line"],
            text=series["oracle_text"],
            mana_cost_dict=CardBlueprint.convert_mana_cost_to_dict(series["mana_cost"])
            if not pd.isna(series["mana_cost"])
            else None,
        )

    @abstractmethod
    def create_new_card_object(self, **kwargs) -> CardObject:
        raise NotImplementedError
