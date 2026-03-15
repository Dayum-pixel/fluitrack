from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from main import get_db
from models import SensorReading, DMA
from schemas import SensorReading, DMA

router = APIRouter(prefix="/api", tags=["sensors"])

@router.get("/dmas", response_model=List[DMA])
def get_dmas(db: Session = Depends(get_db)):
    return db.query(DMA).all()

@router.post("/dmas", response_model=DMA)
def create_dma(dma: DMA, db: Session = Depends(get_db)):
    db_dma = DMA(**dma.dict())
    db.add(db_dma)
    db.commit()
    db.refresh(db_dma)
    return db_dma

@router.get("/readings", response_model=List[SensorReading])
def get_readings(limit: int = 20, db: Session = Depends(get_db)):
    return db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(limit).all()
