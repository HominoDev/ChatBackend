# server/runtime/workers/demo_worker.py
# Libs
import asyncio
import time

# Local modules
from server.runtime.bus import EventBus
from server.runtime.workers.workers_protocol import Worker

class DemoWorker(Worker):
    """
    Воркер на один channel_key.
    Генерирует "demo_tick" раз в 1 сек и публикует в bus.
    """
    def __init__(self, channel_key: str, bus: EventBus) -> None:
        self._channel_key = channel_key
        self._bus = bus
        self._stop = asyncio.Event()

    async def run(self) -> None:
        n = 0
        try:
            while not self._stop.is_set():
                await asyncio.sleep(1)
                n += 1
                await self._bus.publish({
                    "type": "demo_tick",
                    "channel_key": self._channel_key,
                    "n": n,
                    "ts": int(time.time() * 1000),
                    "text": f"tick {n}",
                })
        except asyncio.CancelledError:
            return

    async def stop(self) -> None:
        self._stop.set()