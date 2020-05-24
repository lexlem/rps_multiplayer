import time
from dataclasses import dataclass
from typing import Any, Dict

from logic import Choice, Game, Options, Player, Round


class GameHelper:
    WAIT_BEFORE_CONTINUE = 2  #  sec
    LOOP_SLEEP = 0.1

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
            self.round_duration
        if self.game.current_round and self.round_duration <= 0:
            self.previous_round = self.game.finish_round()
            self.last_action_time = time.time()

    async def play(self, choice: Choice, player: Player) -> None:
        self.game.play(choice, player)

    async def handle_choice(self, choice: str, player: Player) -> None:
        self.play(Choice(choice).value, player)

    async def get_player_stats(self, player: Player) -> Dict[str, int]:
        played_rounds = len(self.game.rounds) or 1
        player_wins = self.game.get_number_of_wins(player)
        return {
            "played_rounds": played_rounds,
            "total_rounds": self.options.rounds,
            "player_wins": player_wins,
        }

    async def start_game(self, app: Any) -> None:
        last_loop_is_required = True
        while self.game.is_running() or last_loop_is_required:
            last_loop_is_required = self.game.is_running()

            self.get_player_stats(player)
            self.handle_choice(choice, player)
            self.finalize_round()
            self.start_next_round()
