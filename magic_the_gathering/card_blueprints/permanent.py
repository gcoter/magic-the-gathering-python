from typing import Dict, Optional

import pandas as pd

from magic_the_gathering.card_blueprints.base import CardBlueprint
from magic_the_gathering.card_objects.base import CardObject
from magic_the_gathering.card_objects.permanent import PermanentObject
from magic_the_gathering.card_objects.state import CardObjectState


class PermanentBlueprint(CardBlueprint):
    def __init__(
        self,
        uuid: str,
        name: str,
        type: str,
        text: str,
        mana_cost_dict: Optional[Dict[str, int]] = None,
        power: Optional[str] = "",
        toughness: Optional[str] = "",
    ):
        super().__init__(uuid=uuid, name=name, type=type, text=text, mana_cost_dict=mana_cost_dict)
        self.power = power
        self.toughness = toughness

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
            power=series["power"] if not pd.isna(series["power"]) else "",
            toughness=series["toughness"] if not pd.isna(series["toughness"]) else "",
        )

    def create_new_card_object(self, state: Optional[CardObjectState] = None) -> CardObject:
        return PermanentObject(
            name=self.name,
            type=self.type,
            text=self.text,
            mana_cost_dict=self.mana_cost_dict,
            power=self.power,
            toughness=self.toughness,
            state=state,
        )
