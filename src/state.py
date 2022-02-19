from inject import instance
import api.ws
import device
from json import dumps, loads
from functools import reduce
from datetime import datetime
import asyncio
from measurements.MeasurementModel import MeasurementModel
from events import EventService
from user.model import UserModel, ProfileModel
import device
from threading import Thread
import playsound

import typedefs


# TODO: now it does not store state, so it must be renamed
class StateService:
    def __init__(self):
        pass
        self.state: typedefs.State = {
            "rfid": 0,
            "door_opened": False,
        }
        self.waiting_for_rfid = False
        self.flag = False

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
            #
            # }
            # TODO: use map again
            # return reduce(lambda acc, item: acc | [{'sensor': item[0], 'time': time.timestamp(), 'value': item[1]}], device_state.items(), dict())
            return device_state


        new_state = map_from_device(device_state)
        old_state = self.state.copy()
        self.state |= new_state

        await self.check_for_events(old_state)
        # for key, value in new_state.items():
        #     asyncio.ensure_future(MeasurementModel.create(time=time.timestamp(), sensor=key, value=value))

        await self.broadcast(new_state)


    async def get_rfid(self):
        if self.waiting_for_rfid:
            raise Exception('Already waiting')
        self.waiting_for_rfid = True
        while (rfid := self.state['rfid']) == 0:
            await asyncio.sleep(0.1)
        self.waiting_for_rfid = False
        return rfid




    async def check_for_events(self, old_state):
        try:
            if not self.state['door_opened'] and not self.waiting_for_rfid:
                if self.state['rfid'] != 0 and old_state['rfid'] == 0:
                    print('rfid here')
                    rfid = self.state['rfid']
                    user = await UserModel.load(profile=ProfileModel).query.where(UserModel.rfid == rfid).gino.all()

                    if len(user) > 0:
                        user = user[0] # type: UserModel
                        print(user.profile.name)
                        await instance(EventService).register_event('RFID', f'Door was opened by {user.profile.name} {user.profile.surname}')
                        asyncio.ensure_future(instance(device.DeviceService).send({'door_opened': True, 'message': f'Welcome, {user.profile.name}'}))

                    else:
                        await instance(EventService).register_event('RFID', f'Unknown card detected, id = {rfid}', True)
                        asyncio.ensure_future(instance(device.DeviceService).send(
                            {'message': f'Access DENIED'}))
                        playsound.playsound('a.wav', block=False)
        except Exception as e:
            print(e)
        # if not self.flag and self.state['weight'] > 900:
        #     await instance(EventService).register_event('weight', f"Patient is to fat: weight = {self.state['weight']}")
        #
        #     self.flag = True
        # if self.state['weight'] <= 900 and self.flag:
        #     self.flag = False



