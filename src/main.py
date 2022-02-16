import asyncio
import json
from inject import Binder, configure, instance
from aiohttp import web
from api import security, routes
from aiohttp_session import session_middleware,SimpleCookieStorage
from gino import Gino
from db import setup_db

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


def start():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(setup_db())

    configure(DI_config)

    websocket_service = instance(api.ws.WebsocketsService)
    device_service = instance(device.DeviceService)
    state_service = instance(state.StateService)

    app = web.Application()

    # TODO: remove SimpleCookieStorage, it is insecure and throws exceptions on /ws
    app.middlewares.append(session_middleware(SimpleCookieStorage()))

    security.setup_security(app)

    app.add_routes([websocket_service.get_route('/ws')] + routes.get_all_routes('/api'))

    app.on_shutdown.append(shutdown)


    asyncio.ensure_future(device_service.get_all())

    for route in app.router.routes():
        if route.method != 'HEAD':
            print(f'{route.method}\t{route.resource.canonical}')

    print('-'*10)

    web.run_app(app, loop=loop, host='0.0.0.0')




if __name__ == '__main__':
    start()
