from inject import instance
import api.ws
import device
from json import dumps, loads
from functools import reduce

import typedefs

class StateService:
    def __init__(self):
        self.state: State = {
            "lamp": False,
            "dimmer": 0,
        }

    async def broadcast(self):
        # map state -> client
        def map_to_client(state: typedefs.State):
            return dumps(state)

        websocket_service = instance(api.ws.WebsocketsService)
        await websocket_service.broadcast(map_to_client(self.state))

    async def on_device_receive(self, device_state: typedefs.DeviceState):
        def map_from_device(state: typedefs.State, device_state: typedefs.DeviceState):
            map = {
                "led": "lamp",
                "pot": "dimmer"
            }

            return state | reduce(lambda acc, item: acc | {map[item[0]]: item[1]}, device_state.items(), dict())

        self.state = map_from_device(self.state, device_state)
        await self.broadcast()
