from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass
class Card:
    uuid: str
    name: str
    types: str
    subtypes: str
    mana_cost: str
    power: int
    toughness: int
    text: str

    @staticmethod
    def from_series(series: pd.Series):
        return Card(
            uuid=series["uuid"],
            name=series["name"],
            types=series["types"],
            subtypes=series["subtypes"],
            mana_cost=series["manaCost"],
            power=series["power"],
            toughness=series["toughness"],
            text=series["text"],
        )

    @property
    def type_list(self) -> List[str]:
        return self.types.split(",")

    @property
    def subtype_list(self) -> List[str]:
        return self.subtypes.split(",")

    @property
    def mana_cost_dict(self) -> Dict[str, int]:
        mana_cost_list = self.mana_cost.replace("{", "").replace("}", " ").strip().split(" ")
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
