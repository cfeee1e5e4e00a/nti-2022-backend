import asyncio
import json
from inject import Binder, configure, instance
from aiohttp import web
from device import DeviceService
from state import StateService


def get_routes(base: str):
    return [
        web.post(base + '/device', devices),
        web.get(base + '/rfid', rfid),
    ]


async def devices(request: web.Request):
    data = await request.json()
    device = instance(DeviceService)
    asyncio.ensure_future(device.send(data))
    return web.HTTPOk()


async def rfid(request: web.Request):
    return web.json_response({'rfid': await instance(StateService).get_rfid()})
