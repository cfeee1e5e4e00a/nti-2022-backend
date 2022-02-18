from inject import instance
import api.ws
import device
from json import dumps, loads
from functools import reduce
from datetime import datetime
import asyncio
from measurements.MeasurementModel import MeasurementModel

import typedefs


# TODO: now it does not store state, so it must be renamed
class StateService:
    def __init__(self):
        pass
        self.state: typedefs.State = {
        }

    async def broadcast(self, state):
        # map state -> client
        def map_to_client(state: typedefs.State):
            return dumps(state)

        websocket_service = instance(api.ws.WebsocketsService)
        await websocket_service.broadcast(map_to_client(state))

    async def on_device_receive(self, device_state: typedefs.DeviceState):
        time = datetime.now()

        def map_from_device(device_state: typedefs.DeviceState):
            # map = {
            #     "led": "lamp",
            #     "pot": "dimmer",
            #     "test": "test",
            # }
            # TODO: use map again
            # return reduce(lambda acc, item: acc | [{'sensor': item[0], 'time': time.timestamp(), 'value': item[1]}], device_state.items(), dict())
            return device_state


        new_state = map_from_device(device_state)
        self.state |= new_state

        for key, value in new_state.items():
            asyncio.ensure_future(MeasurementModel.create(time=time.timestamp(), sensor=key, value=value))

        await self.broadcast(new_state)




