# Libs
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Set
from fastapi import WebSocket
import logging

log = logging.getLogger(__name__)

# Local modules
from server.runtime.bus import EventBus
from server.runtime.workers.workers_protocol import Worker, WorkerFactory

@dataclass
class ChannelState:
    subscribers: Set[WebSocket] = field(default_factory=set)
    worker: Worker | None = None
    worker_task: asyncio.Task | None = None
    idle_task: asyncio.Task | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

class ChannelHub:
    def __init__(self, bus: EventBus, worker_factory: WorkerFactory, idle_ttl_seconds: int = 120) -> None:
        self._bus = bus
        self.worker_factory = worker_factory
        self._idle_ttl = idle_ttl_seconds
        self._channels: Dict[str, ChannelState] = {}

        self._bus.subscribe("demo_tick", self._on_demo_tick)
        self._bus.subscribe("chat_message", self._on_chat_message)

    async def acquire(self, channel_key: str, ws: WebSocket) -> None:
        st = self._channels.get(channel_key)
        if not st:
            st = ChannelState()
            self._channels[channel_key] = st

        async with st.lock:
            st.subscribers.add(ws)

            if st.idle_task:
                st.idle_task.cancel()
                st.idle_task = None

            if not st.worker_task:
                st.worker = DemoWorker(channel_key=channel_key, bus=self._bus)
                st.worker_task = asyncio.create_task(st.worker.run())

    async def release(self, channel_key: str, ws: WebSocket) -> None:
        st = self._channels.get(channel_key)
        if not st:
            return

        async with st.lock:
            st.subscribers.discard(ws)
            if st.subscribers:
                return

            if st.idle_task:
                st.idle_task.cancel()
            st.idle_task = asyncio.create_task(self._idle_stop(channel_key))

    async def _idle_stop(self, channel_key: str) -> None:
        try:
            await asyncio.sleep(self._idle_ttl)
            st = self._channels.get(channel_key)
            if not st:
                return

            async with st.lock:
                if st.subscribers:
                    return
                await self._stop_channel_locked(channel_key, st)
        except asyncio.CancelledError:
            return

    async def _stop_channel_locked(self, channel_key: str, st: ChannelState) -> None:
        if st.worker:
            await st.worker.stop()

        if st.worker_task:
            st.worker_task.cancel()
            try:
                await st.worker_task
            except asyncio.CancelledError:
                pass

        if st.idle_task:
            st.idle_task.cancel()

        self._channels.pop(channel_key, None)

    async def stop_all(self) -> None:
        for channel_key in list(self._channels.keys()):
            st = self._channels.get(channel_key)
            if not st:
                continue
            async with st.lock:
                await self._stop_channel_locked(channel_key, st)

    async def _on_demo_tick(self, ev: dict) -> None:
        channel_key = ev.get("channel_key")
        if not channel_key:
            return

        st = self._channels.get(channel_key)
        if not st or not st.subscribers:
            return

        dead: list[WebSocket] = []
        for ws in list(st.subscribers):
            try:
                await ws.send_json(ev)
            except Exception as e:
                log.warning(f"Failed to send message to WebSocket on channel {channel_key}: {e}")
                dead.append(ws)

        if dead:
            async with st.lock:
                for ws in dead:
                    st.subscribers.discard(ws)
                if not st.subscribers and not st.idle_task:
                    st.idle_task = asyncio.create_task(self._idle_stop(channel_key))
