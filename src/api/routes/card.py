from aiohttp import web
import aiohttp_security
from user.model import UserModel, ProfileModel, MedCardModel
from sqlalchemy import and_


def get_routes(base: str):
    return [
        web.get(base + '/card/{user}', get_card),
        web.post(base + '/card/{user}', post_card),
        web.get(base + '/patients', all_patients),
        web.get(base + '/profile/{login}', patient)
    ]


async def get_user_by_login(login: str) -> UserModel | None:
    users = await UserModel.load(profile=ProfileModel, card=MedCardModel).query.where(UserModel.login==login).gino.all()
    if len(users) > 0:
        return users[0]
    else:
        return None


async def patient(request: web.Request):
    await aiohttp_security.check_authorized(request)
    user = await aiohttp_security.authorized_userid(request)  # type: UserModel
    if user.role != 'doctor' and user.login != request.match_info['login']:
        return web.HTTPUnauthorized(text='You are not doctor')
    patient = await get_user_by_login(request.match_info['login'])
    return web.json_response(patient.profile.toJson())


async def all_patients(request: web.Request):
    await aiohttp_security.check_authorized(request)
    user = await aiohttp_security.authorized_userid(request)  # type: UserModel
    if user.role != 'doctor':
        return web.HTTPUnauthorized(text='You are not doctor')
    patients = await UserModel.load(profile=ProfileModel, card=MedCardModel).query.where(UserModel.role=='patient').gino.all() # type: list[UserModel]
    resp = [{'login':patient.login, 'profile':patient.profile.toJson()} for patient in patients]
    return web.json_response(resp)


async def get_card(request: web.Request):
    await aiohttp_security.check_authorized(request)
    user = await aiohttp_security.authorized_userid(request)  # type: UserModel
    patient_login = request.match_info['user']
    if user.role != 'doctor' and user.login != patient_login:
        return web.HTTPUnauthorized(text='You are not allowed to view this card')
    patient = await get_user_by_login(patient_login)
    if patient.role != 'patient':
        return web.HTTPBadRequest(text='This user doe not have medcard')
    card = patient.card
    return web.json_response({'weight': card.weight, 'assignments': card.assignments})


async def post_card(request: web.Request):
    await aiohttp_security.check_authorized(request)
    user = await aiohttp_security.authorized_userid(request)  # type: UserModel
    if user.role != 'doctor':
        return web.HTTPUnauthorized(text='You are not doctor')
    patient = await get_user_by_login(request.match_info['user'])
    if patient.role != 'patient':
        return web.HTTPBadRequest(text='This user does not have medcard')
    card = patient.card
    data = await request.json() # type: dict
    if 'weight' in data.keys():
        await card.update(weight=float(data['weight'])).apply()
    if 'assignments' in data.keys():
        await card.update(assignments=data['assignments']).apply()
    return web.HTTPOk()
