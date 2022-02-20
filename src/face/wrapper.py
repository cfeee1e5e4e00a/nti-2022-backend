import asyncio
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Process, Queue
from time import sleep
from face.recognizer import VideoThread, create_vt, get_current_face
from asyncio.queues import Queue as AQueue
import cv2
from inject import instance
from state import StateService




class FaceService:
    def __init__(self):
        self.training = False
        self.command_q = Queue(1000)
        self.image_q = Queue(1000)
        self.face_q = Queue(1000)
        self.done_q = Queue(1000)
        self.executor = ThreadPoolExecutor(10, 'queue_reader')
        self.running = True
        asyncio.ensure_future(self.id_worker())
        asyncio.ensure_future(self.image_worker())
        Process(target=self.worker_process).start()
        self.queues = set() # type: set[AQueue]

    def stop(self):
        self.running = False
        self.image_q.close()
        self.face_q.close()
        self.done_q.close()
        self.command_q.put(None)
        self.executor.shutdown(cancel_futures=True, wait=False)

    async def _read_q(self, q: Queue):
        return await asyncio.get_event_loop().run_in_executor(self.executor, q.get)

    async def id_worker(self):
        print('face loop started')
        while self.running:
            msg = await self._read_q(self.face_q)
            await instance(StateService).on_device_receive({'face': msg})
        print('Face loop stopped')

    async def image_worker(self):
        print('face loop started')
        while self.running:
            msg = await self._read_q(self.image_q)
            for q in self.queues:
                await q.put(msg)
        print('Face loop stopped')



    class VideoContext:
        def __init__(self, fs):
            self.fs = fs # type: FaceService

        def __enter__(self):
            q = AQueue(1000)
            self.q = q
            self.fs.queues.add(q)
            return q

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.fs.queues.remove(self.q)

    def get_image_queue(self):
        return self.VideoContext(self)



    async def train_face(self, name):
        if self.training:
            raise Exception('already training')
        self.training = True
        self.command_q.put(name)
        await self._read_q(self.done_q)
        self.training = False
    #
    #
    #
    # async def _train_face_inner(self, name, queue: AQueue):
    #
    #     self.training = True
    #     self.command_q.put(name)
    #
    #     while True:
    #         img = await self._read_q(self.image_q)
    #         if img is None:
    #             print('done')
    #             self.training = False
    #             break
    #         await queue.put(img)
    #     print('done training')
    #     await queue.put(None)


    def worker_process(self):
        print('Face process started')
        vt = create_vt()
        prev_face = None
        while True:
            if not self.command_q.empty():
                cmd = self.command_q.get()
                if cmd == None:
                    break
                else:
                    # start training
                    prev_face = None
                    self.face_q.put(None)
                    vt.start_sampling(cmd)
                    while vt.sampling:
                        self.image_q.put(vt.show_pic())
                        time.sleep(0.005)
                    self.done_q.put('')
            self.image_q.put(vt.show_pic())
            if prev_face != get_current_face():
                prev_face = get_current_face()
                self.face_q.put(prev_face)
            time.sleep(0.005)
            # TODO: fix exceptions in cv2

        print('Face process stopped')



