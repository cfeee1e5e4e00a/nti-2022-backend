import asyncio
import json
from inject import Binder, configure, instance
from aiohttp import web
from device import DeviceService


def get_routes(base: str):
    return [
        web.post(base + '/device', devices),
    ]


async def devices(request: web.Request):
    data = await request.json()
    device = instance(DeviceService)
    asyncio.ensure_future(device.send(data))
    return web.HTTPOk()
