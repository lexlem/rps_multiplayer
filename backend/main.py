import os

from aiohttp import web

from views import wshandler


async def on_shutdown(app):
    for ws in app["sockets"]:
        await ws.close()


def init():
    app = web.Application()
    app["sockets"] = []
    app.router.add_get("/", wshandler)
    app.on_shutdown.append(on_shutdown)
    return app


web.run_app(init())
