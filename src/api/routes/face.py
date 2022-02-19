from aiohttp import web, MultipartWriter
import aiohttp_security
from events import EventModel
from inject import instance
from face.wrapper import FaceService


def get_routes(base: str):
    return [
        web.get(base + '/video', face),
        web.post(base+'/train', train)
    ]


async def train(request: web.Request):
    login = (await request.json())['login']
    await instance(FaceService).train_face(login)
    return web.HTTPOk()


async def face(request: web.Request):
    boundary = "boundarydonotcross"
    resp = web.StreamResponse(status=200, reason='OK', headers={
'Content-Type': 'multipart/x-mixed-replace; '
                        'boundary=--%s' % boundary})
    await resp.prepare(request)
    srv = instance(FaceService)
    with instance(FaceService).get_image_queue() as q:
        while (img := (await q.get())) is not None:
            with MultipartWriter('image/jpeg', boundary=boundary) as mpwriter:

                mpwriter.append(img, {
                    'Content-Type': 'image/jpeg'
                })
                await mpwriter.write(resp, close_boundary=False)
            await resp.drain()

    return resp




