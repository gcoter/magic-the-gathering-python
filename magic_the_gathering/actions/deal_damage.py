from typing import List

from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.kill_player import KillPlayerAction
from magic_the_gathering.actions.move_to_graveyard import MoveToGraveyardAction
from magic_the_gathering.game_state import GameState, ZonePosition


class DealDamageAction(Action):
    @classmethod
    def list_possible_actions(cls, game_state: GameState) -> List[Action]:
        possible_blocker_player_indices = game_state.other_players_blockers.keys()
        return [
            cls(owner="Game", blocker_player_index=blocker_player_index)
            for blocker_player_index in possible_blocker_player_indices
        ]

    def __init__(
        self,
        owner: str,
        blocker_player_index: int,
    ):
        super().__init__(owner=owner)
        self.blocker_player_index = blocker_player_index

    def _execute(self, game_state: GameState) -> GameState:
        blocker_player = game_state.players[self.blocker_player_index]
        assert blocker_player.is_alive
        for attacker_card_uuid, blocker_card_uuids in game_state.other_players_blockers[
            self.blocker_player_index
        ].items():
            attacker_player_index = game_state.current_player_index
            assert attacker_card_uuid in game_state.zones[ZonePosition.BOARD][attacker_player_index]
            attacker_card = game_state.zones[ZonePosition.BOARD][attacker_player_index][attacker_card_uuid]
            attacker_power = attacker_card.get_power()
            if len(blocker_card_uuids) == 0:
                # The player receives the damage directly
                blocker_player.life_points -= attacker_power
                self.logger.info(
                    f"Player {self.blocker_player_index} receives {attacker_power} damage from {attacker_card}"
                )
            else:
                # Blockers deal damage to the attacker
                blocker_power = sum(
                    game_state.zones[ZonePosition.BOARD][self.blocker_player_index][blocker_card_uuid].get_power()
                    for blocker_card_uuid in blocker_card_uuids
                )
                attacker_card.state.damage_marked += blocker_power
                self.logger.info(f"{attacker_card} receives {blocker_power} damage from blockers")

                # Each blocker receives damage from the attacker
                for blocker_card_uuid in blocker_card_uuids:
                    assert blocker_card_uuid in game_state.zones[ZonePosition.BOARD][self.blocker_player_index]
                    blocker_card = game_state.zones[ZonePosition.BOARD][self.blocker_player_index][blocker_card_uuid]
                    blocker_card.state.damage_marked += attacker_power
                    self.logger.info(f"{blocker_card} receives {attacker_power} damage from {attacker_card}")

        # If the player has no more life points, it loses the game
        if blocker_player.life_points <= 0:
            game_state = KillPlayerAction(owner=self.owner, player_index=self.blocker_player_index).execute(game_state)

        # If an attacker received more damage than its toughness, it dies
        for attacker_card_uuid in game_state.zones[ZonePosition.BOARD][attacker_player_index]:
            attacker_player_index = game_state.current_player_index
            assert attacker_card_uuid in game_state.zones[ZonePosition.BOARD][attacker_player_index]
            attacker_card = game_state.zones[ZonePosition.BOARD][attacker_player_index][attacker_card_uuid]
            if attacker_card.state.damage_marked >= attacker_card.get_toughness():
                game_state = MoveToGraveyardAction(
                    owner=self.owner, player_index=attacker_player_index, card_uuid=attacker_card_uuid
                ).execute(game_state)

        # If a blocker received more damage than its toughness, it dies
        for blocker_card_uuid in game_state.zones[ZonePosition.BOARD][self.blocker_player_index]:
            assert blocker_card_uuid in game_state.zones[ZonePosition.BOARD][self.blocker_player_index]
            blocker_card = game_state.zones[ZonePosition.BOARD][self.blocker_player_index][blocker_card_uuid]
            if blocker_card.state.damage_marked >= blocker_card.get_toughness():
                game_state = MoveToGraveyardAction(
                    owner=self.owner, player_index=self.blocker_player_index, card_uuid=blocker_card_uuid
                ).execute(game_state)

        return game_state
