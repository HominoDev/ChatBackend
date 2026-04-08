# server/runtime/workers/twitch_irc_worker.py
# Libs
import asyncio
import time

# Local modules
from server.runtime.bus import EventBus

WORKER_FREQUENCY = 20  # Hz
CYCLE_TIME = 1/WORKER_FREQUENCY  # seconds

class TwitchIRCWorker:
    def __init__(self, channel_key: str, bus: EventBus) -> None:
        self._channel_key = channel_key
        self._bus = bus
        self._stop = asyncio.Event()

    async def run(self) -> None:
        n = 0
        try:
            while not self._stop.is_set():
                await asyncio.sleep(CYCLE_TIME)
                n += 1
                await self._bus.publish({
                    "type": "chat_message",
                    "channel_key": self._channel_key,
                    "n": n,
                    "ts": int(time.time() * 1000),
                    "text": f"tick {n}",
                })
        except asyncio.CancelledError:
            return

    async def stop(self) -> None:
        self._stop.set()
