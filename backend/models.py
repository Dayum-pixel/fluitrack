from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from .main import Base
import enum

class SensorType(enum.Enum):
    FLOW = "flow"
    PRESSURE = "pressure"
    ACOUSTIC = "acoustic"

class DMA(Base):
    __tablename__ = "dmas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # e.g., "DMA-01-Kampala-Central"
    description = Column(String, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    dma_id = Column(Integer, ForeignKey("dmas.id"), nullable=False)
    sensor_type = Column(Enum(SensorType), nullable=False)
    value = Column(Float, nullable=False)  # flow in L/min, pressure in bar, acoustic score 0-100
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    device_id = Column(String, index=True)  # e.g., ESP32 MAC or unique ID
    raw_data = Column(String, nullable=True)  # JSON string for extra fields like battery, GPS

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    dma_id = Column(Integer, ForeignKey("dmas.id"), nullable=False)
    reading_id = Column(Integer, ForeignKey("sensor_readings.id"), nullable=True)
    type = Column(String)  # e.g., "leak_detected", "pressure_drop", "low_flow"
    severity = Column(String)  # "low", "medium", "high"
    confidence_score = Column(Float, default=0.0)
    message = Column(String)
    acknowledged = Column(Integer, default=0)  # 0=false, 1=true
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
