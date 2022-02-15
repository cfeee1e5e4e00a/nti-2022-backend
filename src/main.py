import asyncio
import json
from inject import Binder, configure, instance
from aiohttp import web

import device
import api.ws
import state

def DI_config(binder: Binder):
    binder.bind(api.ws.WebsocketsService, api.ws.WebsocketsService())
    binder.bind(device.DeviceService, device.DeviceService('192.168.2.169', 2000))
    binder.bind(state.StateService, state.StateService())

async def shutdown(_):
    websocket_service = instance(api.ws.WebsocketsService)
    device_service = instance(device.DeviceService)

    await device_service.stop()
    await websocket_service.stop()


if __name__ == '__main__':
    configure(DI_config)

    websocket_service = instance(api.ws.WebsocketsService)
    device_service = instance(device.DeviceService)
    state_service = instance(state.StateService)

    app = web.Application()

    app.add_routes([websocket_service.get_route('/ws')])

    app.on_shutdown.append(shutdown)

    loop = asyncio.get_event_loop()
    web.run_app(app, loop=loop, host='0.0.0.0')
