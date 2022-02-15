import api.routes.auth


def get_all_routes(base):
    return api.routes.auth.get_routes(base + '/auth')