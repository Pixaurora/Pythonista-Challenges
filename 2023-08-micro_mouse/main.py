import asyncio
import importlib
import os
import random
import subprocess
import sys
import time
import traceback
import uuid
from types import ModuleType
from typing import Any, Coroutine, TypeVar


try:
    import aiohttp
    from msgspec.json import decode, encode
except:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            os.path.join(os.path.dirname(__file__), "requirements.txt"),
        ]
    )
    import aiohttp
    from msgspec.json import decode, encode

import event_types


T = TypeVar("T")
DEBUG = os.getenv("DEBUG", False)


class Websocket:
    def __init__(self):
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self.module: ModuleType | None = None
        self.cls: event_types.MicroMouse | None = None

        self.task: asyncio.Task | None = None
        self.user_tasks: list[asyncio.Task] = []
        self.waiters: dict[str, asyncio.Future] = {}

    def run_ws(self):
        asyncio.run(self.start())

    async def start(self):
        self.running = asyncio.Event()
        await self._start_ws()
        await self.reload_code()

        while not self.ws.closed:
            await asyncio.sleep(0)

    def create_user_task(self, task: Coroutine[Any, Any, Any]):
        self.user_tasks.append(asyncio.create_task(task))

    async def broadcast_event(self, event_name: str, data: T):
        if not self.cls:
            print("*****************")
            print(f"Failed to dispatch event, {event_name}, because there is no code loaded!")
            print("*****************")

        if event_name == "position_reset":
            self.create_user_task(self.cls.position_reset(data))
        elif event_name == "start":
            self.create_user_task(self.cls.start(data))
        elif event_name == "end":
            self.create_user_task(self.cls.end(data))
        else:
            print(f"ERROR: unknown event: {event_name}")

    async def reload_code(self):
        try:
            for task in self.user_tasks:
                if not task.done():
                    task.cancel("Reloading your code")

            self.user_tasks = []

            if self.module:
                self.module = importlib.reload(self.module)
            else:
                self.module = importlib.import_module("submission")

            if "MicroMouse" not in dir(self.module):
                raise ValueError(
                    "You do not have a MicroMouse class in your file! If you've changed the name on the example class, you'll need to change it back."
                )

            cls: event_types.MicroMouse = self.module.MicroMouse
            if not issubclass(cls, event_types.MicroMouse):
                raise ValueError(
                    "Your MicroMouse class does not inherit from event_types.MicroMouse. Make sure you subclass event_types.MicroMouse, and then try again"
                )

            self.cls = cls._prepare(self.send_distances, self.send_rot)

        except Exception as e:
            print("*****************")
            print("Failed to (re)load your code!")
            print("Details:\n")
            print("".join(traceback.format_exception(type(e), e, e.__traceback__)))
            print()
            print("Please fix the errors in your code and press reload again!")
            print("*****************")
            self.module = None

    async def _start_ws(self):
        session = aiohttp.ClientSession()
        self.ws = await session.ws_connect("http://127.0.0.1:3456/")
        session.detach()
        self.task = asyncio.create_task(self.pump(), name="Pump Task")

    async def pump(self):
        while self.ws and not self.ws.closed:
            try:
                data = await self.ws.receive_str()
                payload = decode(data, type=event_types.BaseEvent)
            except TypeError:
                print("Unity closed the websocket, shutting down.")
                return
            except Exception as e:
                print(f"Encountered an issue while receiving data from ws: {''.join(traceback.format_exception(type(e), e, e.__traceback__))}")
                continue

            if handler := getattr(self, f"handle_{payload.op}", None):
                if DEBUG:
                    print(data)

                asyncio.create_task(handler(data))

    async def handle_hello(self, payload: str):
        pass

    async def handle_distances(self, payload: str):
        data: event_types.DistancesEvent = decode(payload, type=event_types.DistancesEvent)
        nonce = data.nonce

        if nonce in self.waiters:
            self.waiters[nonce].set_result(data.d)

    async def handle_rot(self, payload: str):
        data: event_types.RotationEvent = decode(payload, type=event_types.RotationEvent)
        nonce = data.nonce

        if nonce in self.waiters:
            self.waiters[nonce].set_result((data.error, data.current))

    async def handle_position_reset(self, payload: str):
        data: event_types.PositionResetEvent = decode(payload, type=event_types.PositionResetEvent)

        await self.broadcast_event("position_reset", data.d)

    async def handle_start(self, payload: str):
        data: event_types.StartEvent = decode(payload, type=event_types.StartEvent)
        await self.broadcast_event("start", data.d.time_remaining)

        if DEBUG:  # epic testing solution
            print("got start!")

            self.running.set()
            last_walls_time = time.time()

            while self.running.is_set():
                distances = await self.send_distances()
                now = time.time()
                if distances.right < 0.7 or distances.left < 0.7:
                    last_walls_time = now

                if distances.right > 0.7 and distances.left > 0.7 and (now - last_walls_time > 0.2) and (0.6 > distances.forward % 0.5 > 0.4):
                    await self.send_rot(random.choice([90, -90]))
                    print("rando!")
                    await asyncio.sleep(0.5)

                if distances.forward < 0.5 and distances.right > 0.7:
                    await self.send_rot(90)
                    print("turn right")
                    await asyncio.sleep(0.5)

                elif distances.forward < 0.5 and distances.left > 0.7:
                    await self.send_rot(-90)
                    print("turn left")
                    await asyncio.sleep(0.5)

                elif distances.forward < 0.5 and distances.left < 0.6 and distances.right < 0.6:
                    await self.send_rot(-180)
                    print("turn around")
                    await asyncio.sleep(0.5)

    async def handle_end(self, payload: str):
        data: event_types.EndEvent = decode(payload, type=event_types.EndEvent)
        await self.broadcast_event("end", data.complete)

        # DEBUG CODE
        self.running.clear()

    async def handle_reload(self, _):
        await self.reload_code()

    async def send_distances(self) -> event_types.DistancesData:
        nonce = str(uuid.uuid4())
        waiter = self.waiters[nonce] = asyncio.Future[event_types.DistancesData]()

        await self.ws.send_str(encode(event_types.DistancesRequest(nonce=nonce, op="distances")).decode())

        return await waiter

    async def send_rot(self, rotation: int):
        nonce = str(uuid.uuid4())
        waiter = self.waiters[nonce] = asyncio.Future[str]()

        await self.ws.send_str(encode(event_types.RotationRequest(nonce=nonce, rot=rotation, op="rot")).decode())

        return await waiter


if __name__ == "__main__":
    main = Websocket()
    main.run_ws()
