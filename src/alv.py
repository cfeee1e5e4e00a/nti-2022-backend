import asyncio
# from datetime import datetime
import state
import typedefs
from inject import instance

class ALVService:
    def __init__(self, host: str = '192.168.1.46', port: int = 2323):
        self._host = host
        self._port = port

        # self._file_name = file_name

        # open(file_name, 'w').close();

        self._running = True

        self._connection_opened = False
        asyncio.ensure_future(self.run())
        print('!!!init')
        self.values = [0.0] * 50

    async def stop(self):
        self._running = False

        if self._connection_opened:
            self._writer.close()
            await self._writer.wait_closed()
        else:
            print(f'Connection not opened')
        
    # async def _write2file(self, time, data: float):
    #     with open('../../' + self._file_name, 'a') as outf:
    #         outf.write(f'{time} {data}\n')
    #     await asyncio.sleep(0.1)

    async def set_state(self, data: float):
        # print(data)
        self.values.pop(0)
        self.values.append(data)
        is_ok = (max(self.values) - min(self.values)) > 0.4
        state_service = instance(state.StateService)
        # print('!!!! alv set state')
        await state_service.on_device_receive({"alv_failed": not is_ok})

    async def run(self):
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        self._connection_opened = True
        print('!!! ALV CONNECTED')
        
        self._writer.write('bondage'.encode('utf-8'))
        await self._writer.drain()

        data = await self._reader.readexactly(27)
            
        # print(f'recieved: {data.decode()!r}')
        
        # buf = f'{data[-2:].decode()}'

        while self._running:
            try:
                res = ''
                while True:
                    try:
                        c = await asyncio.wait_for(self._reader.read(1), timeout=0.1)
                        res += c.decode()
                    except asyncio.TimeoutError:
                        break
                # print(res)
                # await asyncio.sleep(0.1)
                self._writer.write('bondage'.encode('utf-8'))
                await self._writer.drain()

                # data = await self._reader.readexactly(8)
                # data = await self._reader.readuntil(separator=b'.')
                # # data = await self._reader.readline()
                #
                #
                # # print(f'recieved: {buf+data[:-2].decode()!r}')
                #
                # alv_data = float(buf + f'{data[:-2].decode()}')
                # buf = f'{data[-2:].decode()}'

                # print(f'{alv_data=}')

                # now = datetime.now()
                # await self._write2file(now.strftime("%H:%M:%S"), alv_data)

                await self.set_state(float(res))
            except ValueError:
                pass
            except Exception as e:
                print(f'exception: {e!s}')
                await self.stop()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    alv = ALVService()

    loop.run_until_complete(alv.run())

