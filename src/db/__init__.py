from gino import Gino

# TODO: I don't know how to use DI here, so it is singleton
db = Gino()


async def setup_db():
    await db.set_bind('postgresql://nti:nti@127.0.0.1/nti')
    await db.gino.create_all()
