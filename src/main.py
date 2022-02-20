import asyncio
from inject import Binder, configure, instance
from aiohttp import web
from api import security, routes
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage
from aioredis import Redis
from db import setup_db
import os
from pathlib import Path
from dotenv import load_dotenv
import aiohttp_cors
from events import EventService
from face.wrapper import FaceService


os.chdir(Path(__file__).parent.parent)


import device
import api.ws
import state
import alv


def DI_config(binder: Binder):
    binder.bind(EventService, EventService())
    binder.bind(api.ws.WebsocketsService, api.ws.WebsocketsService())
    binder.bind(device.DeviceService, device.DeviceService(os.environ['DEVICE_HOST'], int(os.environ['DEVICE_PORT'])))
    binder.bind(state.StateService, state.StateService())
    binder.bind(alv.ALVService, alv.ALVService())
    binder.bind(FaceService, FaceService())


async def shutdown(_):
    websocket_service = instance(api.ws.WebsocketsService)
    device_service = instance(device.DeviceService)
    alv_service = instance(alv.ALVService)

    await device_service.stop()
    await websocket_service.stop()
    await alv_service.stop()
    instance(FaceService).stop()


def start():
    load_dotenv()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(setup_db())

    configure(DI_config)

    websocket_service = instance(api.ws.WebsocketsService)
    device_service = instance(device.DeviceService)
    state_service = instance(state.StateService)
    alv_service = instance(alv.ALVService)

    app = web.Application()

    app.middlewares.append(session_middleware(RedisStorage(Redis(host=os.environ['REDIS_HOST']), max_age=60*24*365)))

    security.setup_security(app)

    # @web.middleware
    # async def cors_middleware(request, handler):
    #     print('tedfgtrew')
    #     response = await handler(request)
    #     print('resp')
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     return response
    #
    # app.middlewares.append(cors_middleware)


    app.add_routes([websocket_service.get_route('/api/ws')] + routes.get_all_routes('/api'))

    app.on_shutdown.append(shutdown)


    asyncio.ensure_future(device_service.get_all())


    # cors = aiohttp_cors.setup(app, defaults={
    # "http://10.0.228.4:3000": aiohttp_cors.ResourceOptions(
    #         allow_credentials=True,
    #         expose_headers="*",
    #         allow_headers="*",
    #
    #     )})

    for route in app.router.routes():
        # cors.add(route)
        if route.method != 'HEAD':
            print(f'{route.method}\t{route.resource.canonical}')

    print('-'*10)

    app.add_routes([web.static('/static', './samples')])

    web.run_app(app, loop=loop, host='0.0.0.0')




if __name__ == '__main__':
    start()
