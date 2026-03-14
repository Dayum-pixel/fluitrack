from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
import asyncio

from .models import Base, SensorReading, Alert, SensorType
from .mqtt_sub import start_mqtt
from .routers.sensor import router as sensor_router
from .schemas import SensorReading

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})  # Add SSL for Supabase
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@asynccontextmanager
async def lifespan(app: FastAPI):
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
        result = db.execute("SELECT 1").scalar()
        return {"status": "DB connected", "test": result}
    except Exception as e:
        raise HTTPException(500, f"DB failed: {str(e)}")
