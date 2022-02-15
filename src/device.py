import asyncio
from typing import Coroutine, Any
from collections.abc import Callable
import json
from inject import instance
import state

DeviceState = dict[str, object]

# TODO: add tcp reconnect
class DeviceService:
    def __init__(self, host: str, port: int):
        self._running = True
        self._host = host
        self._port = port
        self._ready = asyncio.Lock()
        self._loop = asyncio.get_event_loop()
        self._ready = asyncio.Future()
        self._sent_packet_id = dict()  # type: dict[str, int]
        self._current_id = 0
        asyncio.ensure_future(self._worker())


    async def send(self, data: dict[str, object]):
        #  Sends ONLY latest value
        await self._ready
        data = data.copy()
        while len(data) != 0 and self._running:
            pid = self._current_id
            self._current_id += 1

            for key in data.keys():
                self._sent_packet_id[key] = pid

            print(f'sending {data}')
            await self._send_json(json.dumps(data | {'__inack__': pid}))

            await asyncio.sleep(1)

            for key in list(data.keys()):
                if key not in self._sent_packet_id.keys() or self._sent_packet_id[key] != pid:
                    data.pop(key)

        print('Fully sent data')


    async def stop(self):
        # TODO: close reader and writer
        self._running = False

    async def _send_json(self, msg: str):
        self._writer.write(b'\xff' + f'{len(msg)}{msg}'.encode())
        await self._writer.drain()

    async def set_state(self, device_state: DeviceState):
        state_service = instance(state.StateService)
        await state_service.on_device_receive(device_state)

    async def _worker(self):
        self._reader, self._writer = await asyncio.open_connection(self._host,
                                                                   self._port)  # type: (asyncio.StreamReader, asyncio.StreamWriter)
        self._ready.set_result(None)

        print('in loop')

        while self._running:
            try:
                while (await self._reader.read(1)) != b'\xff' and self._running:
                    pass
                size = int(await self._reader.readline())
                data = await self._reader.readexactly(size)
                print(data)
                # data = json.loads(data.decode())
                # print(data)
                data_decoded = json.loads(data.decode())
                if '__inack__' in data_decoded.keys():
                    for key, value in list(self._sent_packet_id.items()):
                        if value == data_decoded['__inack__']:
                            self._sent_packet_id.pop(key)
                            print(f'removing {key}; ack = {value}')

                await self._send_json(json.dumps({'__ack__': data_decoded['__ack__']}))
                print('calling callback')
                await self.set_state(data_decoded)
            except json.JSONDecodeError:
                pass
