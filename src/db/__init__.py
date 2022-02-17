from gino import Gino
import os

# TODO: I don't know how to use DI here, so it is singleton
db = Gino()


async def setup_db():
    await db.set_bind(os.environ['DB_URL'])
    await db.gino.create_all()
