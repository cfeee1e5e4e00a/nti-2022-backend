import asyncio
from aiohttp import web
from inject import instance
import state
from json import dumps


class WebsocketsService:
    def __init__(self):
        self.clients = set()  # type: set[web.WebSocketResponse]

    async def broadcast(self, data: str):
        # print('broadcasting')
        await asyncio.gather(*[socket.send_str(data) for socket in self.clients])

    async def stop(self):
        await asyncio.gather(*[socket.close() for socket in self.clients])

    def get_route(self, url: str):
        return web.get(url, self._ws_handler)

    async def _ws_handler(self, request: web.Request):
        socket = web.WebSocketResponse()
        await socket.prepare(request)

        self.clients.add(socket)

        await socket.send_str(dumps(instance(state.StateService).state))

        async for msg in socket:
            print(f'Got message: {msg}')

        self.clients.remove(socket)

        return socket
