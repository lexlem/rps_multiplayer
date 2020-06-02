import asyncio
import time
from typing import Any, Dict, List

import config
from logic import Choice, Game, Player


class GameHelper:
    WAIT_BEFORE_CONTINUE = 2
    LOOP_SLEEP = 1

    def __init__(self, game: Game) -> None:
        self.game = game
        self.previous_round = game.start_round()
        self.last_action_time = 0.0
        self.round_duration = config.GAME_ROUND_DURATION

    async def start_next_round(self) -> None:
        if (
            not self.game.is_running()
            or self.game.current_round
            or time.time() - self.last_action_time < self.WAIT_BEFORE_CONTINUE
        ):
            return
        self.game.start_round()
        self.round_duration = config.GAME_ROUND_DURATION

    async def finalize_round(self) -> None:
        self.round_duration -= self.LOOP_SLEEP
        if self.round_duration >= 0:
            await self.send_all(
                message={"action": "timer", "message": self.round_duration}, except_=[]
            )
            await asyncio.sleep(self.LOOP_SLEEP)
        if self.game.current_round and self.round_duration <= 0:
            self.previous_round = self.game.finish_round()
            self.last_action_time = time.time()
            all_players_choices = {
                player.name: player.choice.name.lower() if player.choice else None
                for player in self.game.players
            }
            print(all_players_choices)
            for player in self.game.players:
                await self.send_single(
                    message={
                        "action": "round_result",
                        "message": {
                            "player_result": self.previous_round.get_player_round_result(
                                player=player
                            ).value,
                            "all_players_choices": all_players_choices,
                        },
                    },
                    player=player,
                )

    async def play(self, choice: Choice, player: Player) -> None:
        self.game.play(choice, player)

    async def get_player_stats(self, player: Player) -> None:
        played_rounds = len(self.game.rounds) or 1
        player_wins = self.game.get_number_of_wins(player)
        await self.send_single(
            message={
                "action": "stats",
                "message": {
                    "played_rounds": played_rounds,
                    "total_rounds": config.GAME_ROUNDS_COUNT,
                    "player_wins": player_wins,
                },
            },
            player=player,
        )

    async def send_players_stats(self) -> None:
        for player in self.game.players:
            await self.get_player_stats(player)

    async def start_game(self, app: Any) -> None:
        last_loop_is_required = True
        while self.game.is_running() or last_loop_is_required:
            last_loop_is_required = self.game.is_running()
            await self.finalize_round()
            await self.start_next_round()

    async def send_single(self, message: Dict[str, Any], player: Player) -> None:
        await player.ws.send_json(message)  # type: ignore

    async def send_all(self, message: Dict[str, Any], except_: List[Player]) -> None:
        for player in self.game.players:
            if player not in except_:
                await player.ws.send_json(message)
