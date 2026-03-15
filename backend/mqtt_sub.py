import json
import asyncio
from paho.mqtt import client as mqtt_client
from sqlalchemy.orm import Session
from database import get_db, engine
from models import SensorReading, SensorType
from dotenv import load_dotenv
import os

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "fluitrack/sensors/#")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        print(f"Received: {data} on topic {msg.topic}")

        # Example payload from ESP32: {"device_id": "esp32-01", "dma_id": 1, "type": "flow", "value": 45.2, "raw": "..."}
        dma_id = data.get("dma_id")
        sensor_type_str = data.get("type")
        value = data.get("value")
        device_id = data.get("device_id")

        if not all([dma_id, sensor_type_str, value, device_id]):
            print("Invalid payload")
            return

        sensor_type = SensorType[sensor_type_str.upper()]

        db = next(get_db())  # Get session
        try:
            reading = SensorReading(
                dma_id=dma_id,
                sensor_type=sensor_type,
                value=value,
                device_id=device_id,
                raw_data=payload
            )
            db.add(reading)
            db.commit()
            db.refresh(reading)
            if sensor_type == SensorType.FLOW and value < 5.0:
                alert = Alert(
                    dma_id=dma_id,
                    reading_id=reading.id,
                    type="low_flow_leak",
                    severity="high" if value < 2.0 else "medium",
                    confidence_score=0.85,
                    message=f"Low flow detected in DMA {dma_id}: {value} L/min"
                )
                db.add(alert)
                db.commit()
                print(f"Alert created: {alert.type}")
            print(f"Saved reading ID {reading.id}")
            # TODO: Here we can add leak detection logic / alert creation
        finally:
            db.close()

    except Exception as e:
        print(f"Error processing message: {e}")

def run_mqtt():
    client = mqtt_client.Client(protocol=mqtt_client.MQTTv5)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()  # Enable TLS for port 8883
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_forever()  # Blocking – run in thread later

# For FastAPI startup (we'll add in main.py next)
async def start_mqtt():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_mqtt)
