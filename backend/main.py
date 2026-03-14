from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
import asyncio

from .models import Base
from .mqtt_sub import start_mqtt
from .schemas import SensorReading

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # Create tables if not exist
    asyncio.create_task(start_mqtt())  # Start MQTT in background
    yield

app = FastAPI(title="Fluitrack Backend", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Fluitrack Backend is running! 🚀"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1").scalar()
        return {"status": "Database connected", "test": result}
    except Exception as e:
        raise HTTPException(500, f"DB failed: {str(e)}")

@app.get("/readings/latest", response_model=list[SensorReading])
def get_latest_readings(db: Session = Depends(get_db)):
    readings = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(10).all()
    return readings
