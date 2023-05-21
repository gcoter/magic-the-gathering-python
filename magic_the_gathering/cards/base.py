from typing import Dict, Optional
from uuid import uuid4

import pandas as pd

from magic_the_gathering.cards.state import CardState


class Card:
    @classmethod
    def from_series(cls, series: pd.Series):
        return cls(
            scryfall_uuid=series["id"],
            name=series["name"],
            type=series["type_line"],
            text=series["oracle_text"],
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
        scryfall_uuid: str,
        name: str,
        type: str,
        text: str,
        mana_cost_dict: Optional[Dict[str, int]] = None,
        power: Optional[str] = "",
        toughness: Optional[str] = "",
        state: Optional[CardState] = None,
    ):
        self.uuid = str(uuid4())
        self.scryfall_uuid = scryfall_uuid
        self.name = name
        self.type = type
        self.text = text
        self.mana_cost_dict = mana_cost_dict
        self.power = power
        self.toughness = toughness
        self.state = state

    def create_new_instance(self, state: Optional[CardState] = None):
        return Card(
            scryfall_uuid=self.scryfall_uuid,
            name=self.name,
            type=self.type,
            text=self.text,
            mana_cost_dict=self.mana_cost_dict,
            power=self.power,
            toughness=self.toughness,
            state=state,
        )

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
    def is_permament(self) -> bool:
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
