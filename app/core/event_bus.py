from typing import Dict, List, Callable, Any

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, listener: Callable):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def emit(self, event_type: str, data: Any):
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener(data)