from aiohttp import web
import aiohttp_security

from user.model import UserModel, ProfileModel, MedCardModel


class AuthorizationPolicy(aiohttp_security.AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        return False

    async def authorized_userid(self, identity):
        users = await UserModel.load(profile=ProfileModel, card=MedCardModel).query.where(UserModel.id==int(identity)).gino.all()
        if len(users) > 0:
            return users[0]
        else:
            return None



def setup_security(app: web.Application):
    aiohttp_security.setup(
        app,
        identity_policy=aiohttp_security.SessionIdentityPolicy(),
        autz_policy=AuthorizationPolicy()
    )