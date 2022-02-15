from aiohttp import web

def get_routes(base: str):
    return [
        web.get(base + '/signin', sign_in),
        web.post(base + '/signin', sign_up())
    ]

def sign_in():
    pass

def sign_up():
    pass
