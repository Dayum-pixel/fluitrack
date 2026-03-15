from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy import text

from database import engine, get_db
from mqtt_sub import start_mqtt
from routers.sensor import router as sensor_router
from schemas import SensorReading
from models import SensorReading

app = FastAPI(title="Fluitrack Backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from models import Base
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(start_mqtt())
    yield

app = FastAPI(title="Fluitrack Backend", lifespan=lifespan)

app.include_router(sensor_router)

@app.get("/")
def read_root():
    return {"message": "Fluitrack Backend is running! 🚀"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {"status": "Database connected successfully", "test_query": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {str(e)}")

@app.get("/readings/latest", response_model=list[SensorReading])
def get_latest_readings(db: Session = Depends(get_db)):
    readings = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(10).all()
    return readings
