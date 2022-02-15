import api.routes
from aiohttp import web

def use_routes(app: web.Application):
    app.add_routes(api.routes.get_all_routes('/api'))
