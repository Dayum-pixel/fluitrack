from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy import text
from database import engine, get_db, SessionLocal

from models import Base, SensorReading, Alert, SensorType
from mqtt_sub import start_mqtt
from routers.sensor import router as sensor_router
from schemas import SensorReading

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .models import Base
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(start_mqtt())
    yield

app = FastAPI(title="Fluitrack Backend", lifespan=lifespan)

app.include_router(sensor_router)  # Mount /api routes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Fluitrack Backend running 🚀"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"status": "Database connected successfully", "test_query": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {str(e)}")
