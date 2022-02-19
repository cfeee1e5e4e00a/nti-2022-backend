import asyncio
import time

class ALVService:
    def __init__(self, host: str = '192.168.1.46', port: int = 2323):
        self._host = host
        self._port = port

        self._running = True

        self._connection_opened = False

        asyncio.ensure_future(self._run())

    async def stop(self):
        self._running = False

        if self._connection_opened:
            self._writer.close()
            await self._writer.wait_closed()
        else:
            print(f'Connection not opened')

    async def _run(self):
        while self._running:
            try:
                self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
                self._connection_opened = True

                self._writer.write('bondage'.encode('utf-8'))
                await self._writer.drain()

                data = await self._reader.read()

                print(f'recieved: {data.decode()!r}')

                self._connection_opened = False

            except Exception as e:
                print(f'exception: {str(e)}')
                await self.stop()


async def main():
    alv = ALVService()

    loop = asyncio.get_event_loop()

    end_time = loop.time() + 5

    while True:
        if end_time < loop.time():
            break
        await asyncio.sleep(0.1)

    await alv.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

