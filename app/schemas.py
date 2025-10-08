from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema for health check responses"""

    status: str
    timestamp: datetime


class GenericResponse(BaseModel):
    """Schema for generic API responses"""

    message: str
    data: Optional[Any] = None
    timestamp: datetime
