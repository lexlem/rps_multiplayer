import time
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List

from logic import Choice, Game, Options, Player, Round


class GameHelper:
    WAIT_BEFORE_CONTINUE = 2  #  sec
    LOOP_SLEEP = 1

    def __init__(self, game: Game) -> None:
        self.game = game
        self.options = game.options
        self.previous_round = game.start_round()
        self.last_action_time = 0.0
        self.round_duration = game.options.countdown_duration

    async def start_next_round(self) -> None:
        if (
            not self.game.is_running()
            or self.game.current_round
            or time.time() - self.last_action_time < self.WAIT_BEFORE_CONTINUE
        ):
            return
        self.game.start_round()
        self.round_duration = self.options.countdown_duration

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
            for player in self.game.players:
                await self.send_single(
                    message={
                        "action": "round_result",
                        "message": self.game.get_player_result(player=player).value,
                    },
                    player=player,
                )

    async def play(self, choice: Choice, player: Player) -> None:
        self.game.play(choice, player)

    # async def handle_choice(self, player: Player) -> None:
    #     async for msg in player.ws:
    #         if msg.data["action"] == "choice":
    #             self.play(Choice(msg.data["message"]).value, player)

    # async def handle_choice(self, choice: str, player: Player) -> None:
    #     self.play(Choice(choice).value, player)

    async def get_player_stats(self, player: Player) -> None:
        played_rounds = len(self.game.rounds) or 1
        player_wins = self.game.get_number_of_wins(player)
        await self.send_single(
            message={
                "action": "stats",
                "message": {
                    "played_rounds": played_rounds,
                    "total_rounds": self.options.rounds,
                    "player_wins": player_wins,
                },
            },
            player=player,
        )

    async def start_game(self, app: Any) -> None:
        last_loop_is_required = True
        while self.game.is_running() or last_loop_is_required:
            last_loop_is_required = self.game.is_running()
            await self.finalize_round()
            # for player in self.game.players:
            #     await self.get_player_stats(player)
            await self.start_next_round()

    async def send_single(self, message: Dict[str, Any], player: Player) -> None:
        await player.ws.send_json(message)

    async def send_all(self, message: Dict[str, Any], except_: List[Player]) -> None:
        for player in self.game.players:
            if player not in except_:
                await player.ws.send_json(message)
