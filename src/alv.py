import asyncio
import state
import typedefs
from inject import instance

class ALVService:
    def __init__(self, host: str = '192.168.1.46', port: int = 2323):
        self._host = host
        self._port = port

        self._running = True

        self._connection_opened = False

    async def stop(self):
        self._running = False

        if self._connection_opened:
            self._writer.close()
            await self._writer.wait_closed()
        else:
            print(f'Connection not opened')
        
    async def set_state(self, device_state: typedefs.DeviceState):
        state_service = instance(state.StateService)
        await state_service.on_device_receive(device_state)

    async def run(self):
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        self._connection_opened = True
        
        self._writer.write('bondage'.encode('utf-8'))
        await self._writer.drain()

        data = await self._reader.readexactly(27)
            
        # print(f'recieved: {data.decode()!r}')
        
        while self._running:
            try:
                self._writer.write('bondage'.encode('utf-8'))
                await self._writer.drain()

                data = await self._reader.readexactly(8)
                    
                # print(f'recieved: {data.decode()!r}')

                alv_data = float(data)

                # print(f'{alv_data=}')

                self.set_state({'alv': alv_data})

            except Exception as e:
                print(f'exception: {e!s}')
                await self.stop()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    alv = ALVService()

    loop.run_until_complete(alv.run())

