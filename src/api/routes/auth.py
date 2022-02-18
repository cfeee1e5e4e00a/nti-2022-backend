from aiohttp import web
import aiohttp_security
from user.model import UserModel
from sqlalchemy import and_


def get_routes(base: str):
    return [
        web.post(base + '/signin', sign_in),
        web.post(base + '/signup', sign_up),
        web.get(base + '/logout', logout),
        web.get(base + '/me', info)
    ]


async def info(request: web.Request):
    await aiohttp_security.check_authorized(request)
    user = await aiohttp_security.authorized_userid(request)  # type: UserModel
    return web.json_response({"login": user.login, "id": user.id, "role": user.role})


async def sign_in(request: web.Request):
    data = await request.json()
    login = data['login']
    password = data['password']

    user = await UserModel.query.where(and_(UserModel.login == login,  UserModel.password == password)).gino.first()
    print(user.id, user.login, user.password)
    resp = web.HTTPOk()
    await aiohttp_security.remember(request, resp, str(user.id))
    return resp


async def sign_up(request: web.Request):
    data = await request.json()
    login = data['login']
    password = data['password']
    role = data['role']
    user = await UserModel.create(login=login, password=password, role=role)
    return web.HTTPOk()





async def logout(request: web.Request):
    await aiohttp_security.check_authorized(request)
    resp = web.HTTPOk()
    await aiohttp_security.forget(request, resp)
    raise resp
