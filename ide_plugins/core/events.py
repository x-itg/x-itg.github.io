"""
Event bus for inter-module communication.
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Any, Optional
from enum import Enum
import logging


class EventType(Enum):
    """System event types."""
    # Document events
    DOC_CREATED = "doc:created"
    DOC_MODIFIED = "doc:modified"
    DOC_DELETED = "doc:deleted"
    DOC_HEALTH_CHANGED = "doc:health_changed"
    DOC_REFERENCED = "doc:referenced"
    DOC_WOKEN = "doc:woken"
    
    # Knowledge vitals events
    VITALS_UPDATED = "vitals:updated"
    RISK_DETECTED = "vitals:risk_detected"
    DRIFT_DETECTED = "vitals:drift_detected"
    HEALTH_ALERT = "vitals:health_alert"
    
    # Convergence events
    CONVERGENCE_STARTED = "convergence:started"
    CONVERGENCE_ITERATION = "convergence:iteration"
    CONVERGENCE_COMPLETED = "convergence:completed"
    CONVERGENCE_FAILED = "convergence:failed"
    ARBITRATION_REQUIRED = "convergence:arbitration_required"
    
    # Serial/log events
    LOG_RECEIVED = "log:received"
    POSITIVE_LOG = "log:positive"
    NEGATIVE_LOG = "log:negative"
    EXPECTATION_TIMEOUT = "log:expectation_timeout"
    
    # Schematic events
    SCHEMATIC_LOADED = "schematic:loaded"
    COMPONENT_CLICKED = "schematic:component_clicked"
    CODE_LINK_CLICKED = "schematic:code_link_clicked"
    OCR_COMPLETED = "schematic:ocr_completed"
    
    # Skills events
    SKILL_INVOKED = "skill:invoked"
    SKILL_COMPLETED = "skill:completed"
    SKILL_FAILED = "skill:failed"
    
    # Build events
    BUILD_STARTED = "build:started"
    BUILD_COMPLETED = "build:completed"
    BUILD_FAILED = "build:failed"
    
    # Decision events
    DECISION_CREATED = "decision:created"
    DECISION_SUPERSEDED = "decision:superseded"


@dataclass
class Event:
    """An event in the system."""
    type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = EventType(self.type)


class EventBus:
    """Central event bus for pub-sub communication."""
    
    _instance: Optional['EventBus'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._logger = logging.getLogger(__name__)
        self._async_mode = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            self._logger.debug(f"Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                self._logger.debug(f"Unsubscribed from {event_type.value}")
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        if isinstance(event.type, str):
            event.type = EventType(event.type)
        
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        self._logger.info(f"Event published: {event.type.value}")
        
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    self._logger.error(f"Error in event callback: {e}")
    
    async def publish_async(self, event: Event) -> None:
        """Publish an event asynchronously."""
        if not self._async_mode:
            self._async_mode = True
            self._loop = asyncio.get_event_loop()
        
        if isinstance(event.type, str):
            event.type = EventType(event.type)
        
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        if event.type in self._subscribers:
            tasks = []
            for callback in self._subscribers[event.type]:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(event))
                else:
                    callback(event)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history."""
        if event_type:
            return [
                e for e in self._event_history[-limit:]
                if e.type == event_type
            ]
        return self._event_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    @property
    def subscribed_types(self) -> List[EventType]:
        """Get list of subscribed event types."""
        return list(self._subscribers.keys())


# Global event bus instance
event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return event_bus
