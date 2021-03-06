import api.routes.auth
import api.routes.device
import api.routes.history
import api.routes.journal
import api.routes.face
import api.routes.card

def get_all_routes(base):
    return api.routes.auth.get_routes(base + '/auth') + api.routes.device.get_routes(base) + \
           api.routes.history.get_routes(base) + api.routes.journal.get_routes(base) + api.routes.face.get_routes(base)+ api.routes.card.get_routes(base)