from magic_the_gathering.actions.base import Action
from magic_the_gathering.actions.kill_player import KillPlayerAction
from magic_the_gathering.actions.move_to_graveyard import MoveToGraveyardAction
from magic_the_gathering.game_state import GameState, ZonePosition


class DealDamageAction(Action):
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
        for attacker_card_uuid, blocker_card_uuids in game_state.other_players_blockers[self.blocker_player_index]:
            attacker_player_index = game_state.current_player_index
            assert attacker_card_uuid in game_state.zones[ZonePosition.BOARD][attacker_player_index]
            attacker_card = game_state.zones[ZonePosition.BOARD][attacker_player_index][attacker_card_uuid]
            attacker_power = attacker_card.get_power()
            if len(blocker_card_uuids) == 0:
                # The player receives the damage directly
                blocker_player.life_points -= attacker_power

                # If the player has no more life points, it loses the game
                if blocker_player.life_points <= 0:
                    game_state = KillPlayerAction(owner=self.owner, player_index=self.blocker_player_index).execute(
                        game_state
                    )
            else:
                # Blockers deal damage to the attacker
                blocker_power = sum(
                    game_state.zones[ZonePosition.BOARD][self.blocker_player_index][blocker_card_uuid].get_power()
                    for blocker_card_uuid in blocker_card_uuids
                )
                attacker_card.state.damage_received += blocker_power

                # If the attacker received more damage than its toughness, it dies
                if attacker_card.state.damage_received >= attacker_card.get_toughness():
                    game_state = MoveToGraveyardAction(
                        owner=self.owner, player_index=attacker_player_index, card_uuid=attacker_card_uuid
                    ).execute(game_state)

                # Each blocker receives damage from the attacker
                for blocker_card_uuid in blocker_card_uuids:
                    assert blocker_card_uuid in game_state.zones[ZonePosition.BOARD][self.blocker_player_index]
                    blocker_card = game_state.zones[ZonePosition.BOARD][self.blocker_player_index][blocker_card_uuid]
                    blocker_card.state.damage_received += attacker_power

                    # If a blocker received more damage than its toughness, it dies
                    if blocker_card.state.damage_received >= blocker_card.get_toughness():
                        game_state = MoveToGraveyardAction(
                            owner=self.owner, player_index=self.blocker_player_index, card_uuid=blocker_card_uuid
                        ).execute(game_state)

        return game_state
