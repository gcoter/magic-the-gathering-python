from typing import Dict, Optional

from magic_the_gathering.card_objects.base import CardObject
from magic_the_gathering.card_objects.state import CardObjectState


class PermanentObject(CardObject):
    def __init__(
        self,
        name: str,
        type: str,
        text: str,
        mana_cost_dict: Optional[Dict[str, int]] = None,
        power: Optional[str] = "",
        toughness: Optional[str] = "",
        state: Optional[CardObjectState] = None,
    ):
        super().__init__(name=name, type=type, text=text, mana_cost_dict=mana_cost_dict)
        self.power = power
        self.toughness = toughness
        self.state = state
        if self.state is None:
            self.state = CardObjectState()
