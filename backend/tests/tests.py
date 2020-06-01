from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import request

# loop_context is provided as a utility. You can use any
# asyncio.BaseEventLoop class in its place.
with loop_context() as loop:
    app = _create_example_app()
    with TestClient(TestServer(app), loop=loop) as client:

        async def test_get_route():
            nonlocal client
            resp = await client.get("/")
            assert resp.status == 200
            text = await resp.text()
            assert "Hello, world" in text

        loop.run_until_complete(test_get_route())