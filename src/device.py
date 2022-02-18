import asyncio
from typing import Coroutine, Any
from collections.abc import Callable
import json
from inject import instance
import state
import typedefs
import serial_asyncio
from asyncio.streams import StreamReaderProtocol, StreamReader, StreamWriter
from serial.serialutil import  SerialException
from os import environ
#
# class Protocol(asyncio.Protocol):


# TODO: add tcp reconnect
class DeviceService:
    def __init__(self, host: str, port: int):
        self._running = True
        self._host = host
        self._port = port
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

    async def get_all(self):
        await self.send({'__all__': 1})

    async def set_state(self, device_state: typedefs.DeviceState):
        state_service = instance(state.StateService)
        await state_service.on_device_receive(device_state)

    async def _worker(self):
        # self._reader, self._writer = await asyncio.open_connection(self._host,
        #                                                            self._port)  # type: (asyncio.StreamReader, asyncio.StreamWriter)



        # print('in loop')
        timeout = 0
        while self._running:
            try:
                await self.connect(timeout=timeout)
                while (await self._reader.read(1)) != b'\xff' and self._running:
                    pass
                size = int(await self._reader.readline())
                data = await self._reader.readexactly(size)
                # print(data)
                # data = json.loads(data.decode())
                # print(data)
                data_decoded = json.loads(data.decode())
                if '__inack__' in data_decoded.keys():
                    for key, value in list(self._sent_packet_id.items()):
                        if value == data_decoded['__inack__']:
                            self._sent_packet_id.pop(key)
                            # print(f'removing {key}; ack = {value}')
                if '__ack__' in data_decoded.keys():
                    await self._send_json(json.dumps({'__ack__': data_decoded['__ack__']}))
                # print('calling callback')
                data_decoded.pop('__ack__', None)
                data_decoded.pop('__inack__', None)
                if len(data_decoded.keys()) != 0:
                    print(data_decoded)
                    await self.set_state(data_decoded)
            except json.JSONDecodeError:
                pass
            except UnicodeError:
                pass
            except ValueError:
                pass
            except SerialException as e:
                print(e)
                timeout = 0.1

    async def connect(self, timeout:float = 0):
        self._ready = asyncio.Future()
        await asyncio.sleep(timeout)

        try:
            if self._transport is not None:
                self._transport.close()
        except Exception:
            pass

        self._reader = StreamReader(limit=2 ** 16, loop=self._loop)
        protocol = StreamReaderProtocol(self._reader, loop=self._loop)

        def factory():
            return protocol

        self._transport, _ = await serial_asyncio.create_serial_connection(url=environ['STM_PORT'], baudrate=115200,
                                                                     protocol_factory=factory, loop=self._loop)


        self._writer = StreamWriter(self._transport, protocol, self._reader, self._loop)

        self._ready.set_result(None)

