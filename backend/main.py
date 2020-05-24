import os

from aiohttp import web

from views import wshandler
from game import GameHelper
import config


async def on_shutdown(app):
    for ws in app["sockets"]:
        await ws.close()



def check_room(request):    
    found = None
    for _id, room in rooms.items():
        if len(room.players) < 3:
            found = _id
            break
    else:
        while not found:
            _id = uuid4().hex[:3]
            if _id not in rooms: found = _id


async def game_machine(app):
    while True:
        if len(app["sockets"]) > config.GAME_PLAYERS_COUNT:
            game = Game()
            if args.rounds:
                game.set_options(rounds=float(args.rounds))
            if args.threshold:
                game.set_options(threshold=float(args.threshold))
            if args.countdown:
                game.set_options(countdown_duration=int(args.countdown))
            GameHelper(game).start_game()

            for room.players:
                print("\nGame result for the player: {} \n".format(game.get_player_result().name))

            await ws.send_str(msg.data)


def init():
    app = web.Application()
    app["sockets"] = []
    app.router.add_get("/", wshandler)
    game_machine(app)
    app.on_shutdown.append(on_shutdown)
    return app


web.run_app(init())
