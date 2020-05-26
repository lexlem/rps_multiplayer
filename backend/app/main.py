import asyncio
from aiohttp import web

from views import wshandler


async def on_shutdown(app):
    for player in app["players"]:
        await player.ws.close()


def init():
    app = web.Application()
    app["players"] = []
    app["games"] = []
    app.router.add_get("/", wshandler)
    app.on_shutdown.append(on_shutdown)
    return app


app = init()
web.run_app(app)
