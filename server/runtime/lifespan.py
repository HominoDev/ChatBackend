# server/runtime/lifespan.py
# Libs
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

log = logging.getLogger(__name__)

# Local modules
from server.runtime.registry import Registry
from server.runtime.bus import InMemoryEventBus
from server.runtime.hub import ChannelHub

@asynccontextmanager
async def lifespan(app: FastAPI):
    bus = InMemoryEventBus()
    hub = ChannelHub(bus=bus, idle_ttl_seconds=10)

    app.state.registry = Registry(bus=bus, hub=hub)

    await bus.start()
    log.info("Event bus started")
    try:
        yield
    except Exception as e:
        log.error(f"Error during application lifespan: {e}")
        raise
    finally:
        try:
            await hub.stop_all()
            log.info("Hub stopped")
        except Exception as e:
            log.error(f"Error stopping hub: {e}")
        
        try:
            await bus.stop()
            log.info("Event bus stopped")
        except Exception as e:
            log.error(f"Error stopping event bus: {e}")