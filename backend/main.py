from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from gremlin_python.driver import client, serializer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Backend Taller 5 IoT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = "mongodb+srv://admin_iot:8UemVfllQwCK5S0R@cluster0.itw0467.mongodb.net/?appName=Cluster0"
mongo_client = AsyncIOMotorClient(MONGO_URI)
database = mongo_client.taller_iot 
sensor_collection = database.get_collection("sensor_data")


try:
    gremlin_client = client.Client('ws://localhost:8182/gremlin', 'g')
except Exception as e:
    print("Advertencia: JanusGraph no está corriendo o no se pudo conectar.")

class SensorData(BaseModel):
    deviceId: str
    temperatura: float
    humedad: float
    nivelAgua: int = Field(ge=0, le=4) 

@app.post("/sensor-data")
async def receive_data(data: SensorData):
    data_dict = data.dict()
    
    resultado = await sensor_collection.insert_one(data_dict)
    
    if not resultado.inserted_id:
        raise HTTPException(status_code=500, detail="Error al guardar en MongoDB")

    if data.temperatura > 30.0:
        query_temp = f"g.addV('Alerta').property('tipo', 'Temperatura Alta').property('valor', {data.temperatura}).addE('GENERADA_POR').to(__.V().has('dispositivo', 'id', '{data.deviceId}').fold().coalesce(unfold(), addV('dispositivo').property('id', '{data.deviceId}')))"
        try:
            gremlin_client.submit(query_temp)
        except Exception:
            pass

    if data.nivelAgua <= 1:
        query_agua = f"g.addV('Alerta').property('tipo', 'Nivel Agua Bajo').property('valor', {data.nivelAgua}).addE('GENERADA_POR').to(__.V().has('dispositivo', 'id', '{data.deviceId}').fold().coalesce(unfold(), addV('dispositivo').property('id', '{data.deviceId}')))"
        try:
            gremlin_client.submit(query_agua)
        except Exception:
            pass

    return {"status": "success", "message": "Datos procesados en Mongo y grafos evaluados"}

@app.get("/historico")
async def get_historico():
    cursor = sensor_collection.find().sort("_id", -1).limit(10)
    datos = await cursor.to_list(length=10)
    for d in datos:
        d["_id"] = str(d["_id"])
    return datos