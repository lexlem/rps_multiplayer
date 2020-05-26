import os
import random
import asyncio
from aiohttp import web

from config import GAME_PLAYERS_COUNT
from game import GameHelper
from logic import Player, Game

WS_FILE = os.path.join(os.path.dirname(__file__), "index.html")


async def wshandler(request):
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    new_player = Player()
    new_player.ws = resp

    try:
        print("New player joined.")
        for player in request.app["players"]:
            await player.ws.send_str("New player joined")
        request.app["players"].append(new_player)

        if len(request.app["players"]) >= GAME_PLAYERS_COUNT:
            participating_players = random.sample(
                request.app["players"], GAME_PLAYERS_COUNT
            )
            game = Game(players=participating_players)
            request.app["games"].append(game)
            request.app["players"] = list(
                set(request.app["players"]) - set(participating_players)
            )
            for player in participating_players:
                await player.ws.send_json(
                    {"action": "game_start", "message": "Game started",}
                )
            await GameHelper(game).start_game(request.app)
            for player in game.players:
                await player.ws.send_json(
                    {
                        "action": "game_result",
                        "message": str(game.get_player_result(player).name),
                    }
                )
                request.app["players"].append(player)

        async for msg in new_player.ws:
            if msg.type == web.WSMsgType.TEXT:
                for player in request.app["players"]:
                    if player.ws is not new_player.ws:
                        await player.ws.send_json(
                            {
                                "action": "choice",
                                "player": player.name,
                                "message": msg.data,
                            }
                        )
            else:
                return new_player.ws
        return new_player.ws

    finally:
        if new_player in request.app["players"]:
            request.app["players"].remove(new_player)
            print("Someone disconnected.")
            for player in request.app["players"]:
                await player.ws.send_str("Someone disconnected.")
