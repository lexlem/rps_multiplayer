from aiohttp import web
from aiojobs.aiohttp import setup

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


if __name__ == "__main__":
    app = init()
    setup(app)
    web.run_app(app)
