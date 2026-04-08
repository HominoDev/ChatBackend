# server/runtime/bus.py
# Libs
import asyncio
from typing import Awaitable, Callable, Dict, List, Any


Event = dict
EventHandler = Callable[[Event], Awaitable[None]]

class EventBus:
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def subscribe(self, event_type: str, handler: EventHandler) -> None: ...
    async def publish(self, event: Event) -> None: ...

class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._q: asyncio.Queue[Event] = asyncio.Queue()
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: Event) -> None:
        await self._q.put(event)

    async def start(self) -> None:
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        try:
            while not self._stop.is_set():
                ev = await self._q.get()
                et = ev.get("type")
                for h in self._handlers.get(et, []):
                    try:
                        await h(ev)
                    except Exception:
                        # логирование добавишь отдельно
                        pass
        except asyncio.CancelledError:
            return
