from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from time import time
from typing import DefaultDict, List, Optional, Union, cast

from aiohttp import web

import config


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

    def __key(self):
        return (
            self.cuttable,
            self.wrappable,
            self.crushable,
            self.can_wrap,
            self.can_crush,
            self.can_cut,
        )

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Weapon):
            return self.__key() == other.__key()
        return NotImplemented

    def encounter(self, weapons: List["Weapon"]) -> Result:
        result = self.draw(weapons) or self.lose(weapons) or Result.WIN
        assert result is not None
        return result

    def draw(self, weapons: List["Weapon"]) -> Optional[Result]:
        if len(weapons) == 1:
            return Result.DRAW if self == weapons[0] else None
        else:
            all_weapons = weapons[:]
            all_weapons.append(self)
            return (
                Result.DRAW
                if (
                    len(set(all_weapons)) <= 1
                    or (
                        any(weapon.can_cut for weapon in all_weapons)
                        and any(weapon.can_crush for weapon in all_weapons)
                        and any(weapon.can_wrap for weapon in all_weapons)
                    )
                )
                else None
            )

    def lose(self, weapons: List["Weapon"]) -> Optional[Result]:
        return (
            Result.LOSE
            if (
                (self.cuttable and any(weapon.can_cut for weapon in weapons))
                or (self.crushable and any(weapon.can_crush for weapon in weapons))
                or (self.wrappable and any(weapon.can_wrap for weapon in weapons))
            )
            else None
        )


class Choice(Enum):
    ROCK = Weapon(wrappable=True, can_crush=True)
    PAPER = Weapon(cuttable=True, can_wrap=True)
    SCISSORS = Weapon(crushable=True, can_cut=True)


@dataclass(eq=False)
class Player:
    choice: Optional[Choice] = None
    name: str = "Player"
    ws: Optional[web.WebSocketResponse] = None
    game: Optional["Game"] = None

    def get_selected_weapon(self) -> Optional[Weapon]:
        return cast(Weapon, self.choice.value) if self.choice else None

    def set_choice(self, choice: Choice) -> None:
        self.choice = choice

    def reset_choice(self) -> None:
        self.choice = None


class Round:
    timings: DefaultDict[Player, float] = defaultdict()

    def __init__(self, players: List[Player]):
        self.players = players
        for player in self.players:
            player.reset_choice()
        self.winners: List[Player] = []
        self.draw: bool = False

    def play(self, player: Player, choice: Choice) -> None:
        self.timings[player] = time()
        if not player.choice:
            player.set_choice(choice)

    def finalize(self, forfeited_player: Optional[Player] = None) -> None:
        if not forfeited_player:
            if not self.find_winner_by_timing():
                weapons = {
                    player: player.get_selected_weapon() for player in self.players
                }
                for player in self.players:
                    enemy_weapons = [
                        weapon for enemy, weapon in weapons.items() if enemy != player
                    ]
                    player_result = player.get_selected_weapon().encounter(
                        enemy_weapons
                    )
                    if player_result == Result.WIN:
                        self.winners.append(player)
                    elif player_result == Result.DRAW:
                        self.draw = True
                        break
        else:
            for player in self.players:
                if player != forfeited_player:
                    self.winners.append(player)

    def played_on_time(self, player: Player, end_time: float) -> bool:
        NO_TIME = 0
        return (
            end_time - config.GAME_ROUND_DURATION
            < self.timings.get(player, NO_TIME)
            < end_time
        )

    def find_winner_by_timing(self) -> bool:
        end_time = time()
        players_on_time = {
            player: self.played_on_time(player, end_time) for player in self.players
        }
        if all(players_on_time.values()):
            return False
        elif not any(players_on_time.values()):
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

    def get_player_round_result(self, player: Player) -> Result:
        if self.draw:
            return Result.DRAW
        else:
            if player in self.winners:
                return Result.WIN
            else:
                return Result.LOSE


class Game:
    def __init__(self, players):
        self.players = players
        self.winners: List[Player] = []
        self.game_rounds_count = config.GAME_ROUNDS_COUNT
        self.rounds: List[Round] = []
        self.current_round: Union[Round, None]
        self.isForfeited = False
        for player in players:
            player.game = self

    def is_running(self) -> bool:
        if not self.isForfeited:
            return len(self.rounds) < self.game_rounds_count
        else:
            return False

    def all_players_played(self) -> bool:
        return all([player.choice for player in self.players])

    async def play(self, choice: Choice, player: Player) -> None:
        if self.current_round:
            self.current_round.play(player, choice)

    async def forfeit(self, player: Player) -> None:
        self.winners = [winner for winner in self.players if winner != player]
        self.finish_round()
        self.isForfeited = True

    def start_round(self) -> Round:
        if self.is_running():
            self.current_round = Round(players=self.players)
            return self.current_round
        else:
            raise GameError("Game already finished")

    def check_for_winner(self) -> None:
        if self.is_running():
            return

        if not self.isForfeited:
            player_wins = {
                player: self.get_number_of_wins(player) for player in self.players
            }
            max_wins = max(player_wins.values())
            max_wins_players = [
                player for player, wins in player_wins.items() if wins == max_wins
            ]
            self.winners = max_wins_players

    def finish_round(self, forfeited_player: Optional[Player] = None) -> Round:
        assert self.current_round is not None
        finished_round = self.current_round
        finished_round.finalize(forfeited_player)
        self.rounds.append(finished_round)
        if finished_round.draw:
            self.game_rounds_count += 1
        self.current_round = None
        self.check_for_winner()
        return finished_round

    def get_number_of_wins(self, player: Player) -> int:
        return sum([1 for round in self.rounds if player in round.winners])

    def get_player_result(self, player: Player) -> Result:
        if not self.isForfeited:
            player_wins = self.get_number_of_wins(player)
            max_wins = max([self.get_number_of_wins(player) for player in self.players])
            if max_wins == 0:
                return Result.DRAW
            else:
                if player_wins == max_wins:
                    return Result.WIN
                else:
                    return Result.LOSE
        else:
            if player in self.winners:
                return Result.WIN
            else:
                return Result.LOSE
