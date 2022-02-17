from aiohttp import web
from measurements.MeasurementModel import MeasurementModel
from json import loads, dumps


def get_routes(base: str):
    return [
        web.get(base + '/history', history),
    ]


async def history(request: web.Request):
    data = await MeasurementModel.query.gino.all()  # type: list[MeasurementModel]
    return web.json_response(sorted(list(map(lambda a: {'sensor': a.sensor, 'time': a.time, 'value': a.value}, data)), key=lambda a: a['time']))