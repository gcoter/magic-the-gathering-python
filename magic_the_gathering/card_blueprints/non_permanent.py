from magic_the_gathering.card_blueprints.base import CardBlueprint
from magic_the_gathering.card_objects.base import CardObject
from magic_the_gathering.card_objects.non_permanent import NonPermanentObject


class NonPermanentBlueprint(CardBlueprint):
    def create_new_card_object(self) -> CardObject:
        return NonPermanentObject(name=self.name, type=self.type, text=self.text, mana_cost_dict=self.mana_cost_dict)
