import os
import random
import json
import asyncio
from aiohttp import web
from aiojobs.aiohttp import spawn

from config import GAME_PLAYERS_COUNT
from game import GameHelper
from logic import Player, Game, Choice

WS_FILE = os.path.join(os.path.dirname(__file__), "index.html")


async def game_handler(request):
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

        await spawn(request, game_handler(request))

        async for msg in new_player.ws:
            if msg.type == web.WSMsgType.TEXT:
                message_data = json.loads(msg.data)
                if message_data.get("action") == "choice":
                    await new_player.game.play(Choice[message_data["message"].upper()], new_player)
                else:
                    for player in request.app["players"]:
                        if player.ws is not new_player.ws:
                            await player.ws.send_json(
                                {
                                    "action": "message",
                                    "player": new_player.name,
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
