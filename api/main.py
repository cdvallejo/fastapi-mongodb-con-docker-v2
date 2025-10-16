from datetime import date
from fastapi import FastAPI, HTTPException
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List

class Obra(BaseModel):
  titulo: str
  compositor: List[str]
  libretista: List[str]
  año: int
  genero: str

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["teatro_lirico"]

@app.get("/")
async def root():
  return{"ok": True, "Colecciones": await db.list_collection_names()}

# Endpoint para listar todas las obras
@app.get("/obras", response_description="Lista de obras", response_model=List[Obra])
async def list_obras():
  obras = await db["obras"].find().to_list(100)
  return obras

# Endpoint para crear una nueva obra
@app.post("/obras", response_description="Agrega una nueva obra", response_model=Obra)
async def create_obra(obra: Obra):
  obra_dict = obra.dict()
  await db["obras"].insert_one(obra_dict)
  return obra

# Endpoint para obtener los datos de una obra por su título
@app.get("/obra/{titulo}", response_description="Obtiene una obra específica con el título", response_model=Obra)
async def find_by_titulo_obra(titulo: str):
  obra = await db["obras"].find_one({"titulo": titulo})
  if obra is not None:
    return obra
  else:
    raise HTTPException(status_code=404, detail=f"Obra con título {titulo} no encontrado en la base de datos.")
  
# Endpoint para borrar una específica por título
@app.delete("/obra/{titulo}", response_description="Borra una obra específica con el título")
async def delete_obra(titulo: str):
  delete_result = await db["obras"].delete_one({"titulo": titulo})
  if delete_result.deleted_count == 0:
    raise HTTPException(status_code=404, detail=f"Obra con título {titulo} no encontrado en la base de datos.")
  else:
    return {"message": "Título borrado con éxito"}