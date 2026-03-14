from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DMABase(BaseModel):
    name: str
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None

class DMACreate(DMABase):
    pass

class DMA(DMABase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SensorReadingBase(BaseModel):
    dma_id: int
    sensor_type: str
    value: float
    device_id: str
    raw_data: Optional[str] = None

class SensorReadingCreate(SensorReadingBase):
    pass

class SensorReading(SensorReadingBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    dma_id: int
    type: str
    severity: str
    confidence_score: float = 0.0
    message: str
    acknowledged: int = 0

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    reading_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
