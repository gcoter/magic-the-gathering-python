from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd


@dataclass
class Card:
    uuid: str
    name: str
    type_line: str
    text: str
    mana_cost: Optional[str] = ""
    power: Optional[str] = ""
    toughness: Optional[str] = ""

    @staticmethod
    def from_series(series: pd.Series):
        return Card(
            uuid=series["id"],
            name=series["name"],
            type_line=series["type_line"],
            text=series["oracle_text"],
            mana_cost=series["mana_cost"] if not pd.isna(series["mana_cost"]) else "",
            power=series["power"] if not pd.isna(series["power"]) else "",
            toughness=series["toughness"] if not pd.isna(series["toughness"]) else "",
        )

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
