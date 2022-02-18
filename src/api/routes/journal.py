from aiohttp import web
import aiohttp_security
from events import EventModel


def get_routes(base: str):
    return [
        web.get(base + '/journal/{tag}', journal),
    ]


async def journal(request: web.Request):
    data = await EventModel.query.where(EventModel.tag == request.match_info['tag']).gino.all()
    return web.json_response(sorted(list(map(lambda m: {'time': m.time, 'data':m.data}, data)), key=lambda a: a['time']))