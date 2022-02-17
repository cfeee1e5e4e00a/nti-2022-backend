import api.routes.auth
import api.routes.device
import api.routes.history

def get_all_routes(base):
    return api.routes.auth.get_routes(base + '/auth') + api.routes.device.get_routes(base) + api.routes.history.get_routes(base)