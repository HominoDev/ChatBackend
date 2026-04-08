# server/runtime/registry.py
# Libs
from dataclasses import dataclass

# Local modules
from server.runtime.bus import EventBus
from server.runtime.hub import ChannelHub

@dataclass(slots=True)
class Registry:
    bus: EventBus
    hub: ChannelHub