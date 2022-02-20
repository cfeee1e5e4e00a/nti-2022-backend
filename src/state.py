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
import transliterate

import typedefs


# TODO: now it does not store state, so it must be renamed
class StateService:
    def __init__(self):
        pass
        self.state: typedefs.State = {
            "rfid": 0,
            "door_opened": False,
            "face": None
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

        await self.check_for_events(old_state, new_state)
        # for key, value in new_state.items():
        #     asyncio.ensure_future(MeasurementModel.create(time=time.timestamp(), sensor=key, value=value))

        await self.broadcast(new_state)


    async def get_rfid(self):
        # if self.waiting_for_rfid:
        #     raise Exception('Already waiting')
        self.waiting_for_rfid = True
        while (rfid := self.state['rfid']) == 0:
            await asyncio.sleep(0.1)
        self.waiting_for_rfid = False
        return rfid




    async def check_for_events(self, old_state, diff):
        try:
            if 'alarm' in diff.keys():
                if diff['alarm']:
                    await instance(EventService).register_event('ALARM',f'Alarm was triggered', False)
            if 'alv_failed' in old_state.keys() and 'alv_failed' in diff.keys():
                if diff['alv_failed'] and not old_state['alv_failed']:
                    await instance(EventService).register_event('ALV', f'ALV failed', False)
            if not self.state['door_opened'] and not self.waiting_for_rfid:
                if self.state['rfid'] != 0 and old_state['rfid'] == 0:
                    print('rfid here')
                    rfid = self.state['rfid']
                    user = await UserModel.load(profile=ProfileModel).query.where(UserModel.rfid == rfid).gino.all()

                    if len(user) > 0:
                        user = user[0] # type: UserModel
                        print(user.profile.name)
                        await instance(EventService).register_event('RFID', f'Door was opened by {user.profile.name} {user.profile.surname}')
                        await self.open_door(user)

                    else:
                        await instance(EventService).register_event('RFID', f'Unknown card detected, id = {rfid}', True)
                        await self.fail_door()

            # TODO: only open when button pressed
            if not self.state['door_opened'] and 'face' in diff.keys():
                if (face := diff['face']) is not None:
                    users = await UserModel.load(profile=ProfileModel).query.where(
                        UserModel.login == str(face)).gino.all()
                    if len(users) > 0:
                        user = users[0]
                        await instance(EventService).register_event('FACE', f'Door opened by {user.profile.name} {user.profile.surname}')
                        await self.open_door(user)
        except Exception as e:
            print(e)
            # raise e

    async def open_door(self, user: UserModel):
        asyncio.ensure_future(instance(device.DeviceService).send({'door_opened': True, 'message': f'Welcome, {transliterate.translit(user.profile.name, "ru", reversed=True)}'}))

    async def fail_door(self):
        asyncio.ensure_future(instance(device.DeviceService).send({'message': f'Access DENIED'}))
        playsound.playsound('a.wav', block=False)



