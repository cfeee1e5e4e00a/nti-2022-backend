import api.routes.auth
import api.routes.device

def get_all_routes(base):
    return api.routes.auth.get_routes(base + '/auth') + api.routes.device.get_routes(base)