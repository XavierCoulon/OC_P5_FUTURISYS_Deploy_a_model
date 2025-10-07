from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Schema for health check responses"""
    status: str
    timestamp: datetime


class GenericResponse(BaseModel):
    """Schema for generic API responses"""
    message: str
    data: Optional[Any] = None
    timestamp: datetime