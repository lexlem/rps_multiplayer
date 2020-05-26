import random
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any, DefaultDict, List, Optional, Set, Type, Union, cast

from aiohttp import web


class PlayerError(Exception):
    pass


class GameError(Exception):
    pass


class Result(Enum):
    DRAW = 0
    WIN = 1
    LOSE = -1


@dataclass
class Weapon:
    cuttable: bool = False
    wrappable: bool = False
    crushable: bool = False
    can_wrap: bool = False
    can_crush: bool = False
    can_cut: bool = False

    def encounter(self, weapons: List["Weapon"]) -> Result:
        result = self.lose(weapons) or self.draw(weapons) or Result.WIN
        assert result is not None
        return result

    def draw(self, weapons: List["Weapon"]) -> Optional[Result]:
        return (
            Result.DRAW if (len(set(weapons)) <= 1 or len(set(weapons)) == 3) else None
        )

    def lose(self, weapons: List["Weapon"]) -> Optional[Result]:
        return (
            Result.LOSE
            if (
                (self.cuttable and all(weapon.can_cut for weapon in weapons))
                or (self.crushable and all(weapon.can_crush for weapon in weapons))
                or (self.wrappable and all(weapon.can_wrap for weapon in weapons))
            )
            else None
        )


class Choice(Enum):
    ROCK = Weapon(wrappable=True, can_crush=True)
    PAPER = Weapon(cuttable=True, can_wrap=True)
    SCISSORS = Weapon(crushable=True, can_cut=True)


@dataclass
class Options:
    countdown_duration: float = 10
    rounds: int = 3
    threshold: float = 0.5

    def set(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            try:
                getattr(self, key)
                setattr(self, key, value)
            except AttributeError:
                raise AttributeError("Cannot set non existing option: {}".format(key))


@dataclass(eq=False)
class Player:
    choice: Optional[Choice] = None
    name: str = "Player"
    ws: Optional[web.WebSocketResponse] = None
    game: Optional["Game"] = None

    def get_selected_weapon(self) -> Optional[Weapon]:
        return cast(Weapon, self.choice.value) if self.choice else None

    def set_choice(self, choice_choice: Choice) -> None:
        self.choice = choice_choice

    def reset_choice(self) -> None:
        self.choice = None


class Round:
    timings: DefaultDict[Player, float] = defaultdict(float)

    def __init__(self, players: List[Player], options: Options):
        self.players = players
        map(lambda player: player.reset_choice, self.players)
        self.options = options
        self.winners: List[Player] = []
        self.draw: bool = False

    def play(self, player: Player, choice: Choice) -> None:
        self.timings[player] = time()
        if not player.choice:
            player.set_choice(choice)

    def finalize(self) -> None:
        if not self.find_winner_by_timing():
            weapons = [player.get_selected_weapon() for player in self.players]
            for player in self.players:
                player_result = player.get_selected_weapon().encounter(weapons)
                if player_result == Result.WIN:
                    self.winners.append(player)
                elif player_result == Result.DRAW:
                    self.draw = True
                    break

    def played_on_time(self, player: Player, end_time: float) -> bool:
        NO_TIME = 0
        return (
            end_time - self.options.threshold
            < self.timings.get(player, NO_TIME)
            < end_time + self.options.threshold
        )

    def find_winner_by_timing(self) -> bool:
        end_time = time()
        players_on_time = {
            player: self.played_on_time(player, end_time) for player in self.players
        }
        if all(players_on_time.values()):
            return False
        elif not all(players_on_time.values()):
            self.draw = True
        else:
            played_players = {
                player for player, on_time in players_on_time.items() if on_time
            }
            if len(played_players) == 1:
                self.winners.append(played_players.pop())
            else:
                return False
        return bool(self.winners or self.draw)


@dataclass
class GameRoom:
    _players: Set[Player] = field(init=False)

    @staticmethod
    def get(room_id):
        return room_id

    def send_all(self, message: str, except_: List[Player]) -> None:
        for player in self.players:
            if player not in except_:
                player.ws.send_str(message)

    @property
    def players(self):
        return frozenset(self._players)

    def add_player(self, player: Player) -> None:
        self._players.add(player)

    def remove_player(self, player: Player) -> None:
        self._players.remove(player)


class Game:
    def __init__(self, players):
        self.options = Options()
        self.players = players
        self.winner: Optional[Player] = None
        self.rounds: List[Round] = []
        self.current_round: Union[Round, None]

    def set_options(self, **kwargs: Any) -> None:
        self.options.set(**kwargs)

    def is_running(self) -> bool:
        return len(self.rounds) < self.options.rounds

    def all_players_played(self) -> bool:
        return all([player.choice for player in self.players])

    def play(self, choice: Choice, player: Player) -> None:
        if self.current_round:
            self.current_round.play(player, choice)

    def start_round(self) -> Round:
        if self.is_running():
            self.current_round = Round(players=self.players, options=self.options)
            return self.current_round
        else:
            raise GameError("Game already finished")

    def check_for_winner(self) -> None:
        if self.is_running():
            return
        player_wins = {
            player: self.get_number_of_wins(player) for player in self.players
        }
        max_wins = max(player_wins.values())
        max_wins_players = [
            player for player, wins in player_wins.items() if wins == max_wins
        ]
        if len(max_wins_players) > 1:
            return
        else:
            self.winner = max_wins_players[0]

    def finish_round(self) -> Round:
        assert self.current_round is not None
        finished_round = self.current_round
        finished_round.finalize()
        self.rounds.append(finished_round)
        self.current_round = None
        self.check_for_winner()
        return finished_round

    def get_number_of_wins(self, player: Player) -> int:
        return sum([1 for round in self.rounds if player in round.winners])

    def get_player_result(self, player: Player) -> Result:
        player_wins = self.get_number_of_wins(player)
        max_wins = max([self.get_number_of_wins(player) for player in self.players])
        if player_wins == max_wins:
            return Result.WIN
        else:
            return Result.LOSE
