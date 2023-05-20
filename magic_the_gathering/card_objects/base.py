from typing import Dict, Optional
from uuid import uuid4


class CardObject:
    def __init__(
        self,
        name: str,
        type: str,
        text: str,
        mana_cost_dict: Optional[Dict[str, int]] = None,
    ):
        self.uuid = str(uuid4())
        self.name = name
        self.type = type
        self.text = text
        self.mana_cost_dict = mana_cost_dict
