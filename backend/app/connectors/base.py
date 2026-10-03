from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class SourceLabel(str, Enum):
    OFFICIAL = "OFFICIAL"
    GOVERNMENT_OPEN_DATA = "GOVERNMENT OPEN DATA"
    AUTHORIZED_API = "AUTHORIZED API"
    LICENSED_PROVIDER = "LICENSED PROVIDER"
    USER_PROVIDED = "USER PROVIDED"
    DERIVED = "DERIVED"
    UNAVAILABLE = "UNAVAILABLE"

class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    NOT_CONFIGURED = "NOT CONFIGURED"

class ConnectorHealth(BaseModel):
    name: str
    status: HealthStatus
    latency_ms: int
    last_checked: datetime
    message: Optional[str] = None
    records_synced: Optional[int] = 0

class BaseConnector(ABC):
    def __init__(self, name: str, source_type: SourceLabel, priority: int):
        self.name = name
        self.source_type = source_type
        self.priority = priority

    @abstractmethod
    async def health_check(self) -> ConnectorHealth:
        pass
