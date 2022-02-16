from aiohttp import web
import aiohttp_security

from user.model import UserModel


class AuthorizationPolicy(aiohttp_security.AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        return False

    async def authorized_userid(self, identity):
        return await UserModel.get(int(identity))


def setup_security(app: web.Application):
    aiohttp_security.setup(
        app,
        identity_policy=aiohttp_security.SessionIdentityPolicy(),
        autz_policy=AuthorizationPolicy()
    )