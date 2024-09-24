from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import database as db
from models import MeasurementPeriodEnum
from typing import List


# Allow CORS for your frontend URL
origins = [
    "http://localhost:3000",  # Frontend URL
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI with PostgreSQL!"}

@app.get("/tickers")
async def read_tickers():
    tickers = db.get_tickers()
    return {"tickers": tickers}


@app.post("/create_universe")
async def create_universe(body: db.CreateUniverseRequestBody):
    print(body)
    universe = db.post_create_universe(body)
    return {"universe": universe}


@app.get("/get_universes")
async def read_universes():
    universes = db.get_universes()
    return {"universes": universes}


@app.put("/edit_universe/{universe_id}")
def edit_universe(universe_id: int, body: db.EditUniverseRequestBody):
  universe = db.update_universe(universe_id, body)
  return {"universe": universe}


@app.get("/measurement_periods", response_model=List[int])
async def get_measurement_periods():
    """
    Return the allowed measurement period values as a list of integers
    """
    return [period.value for period in MeasurementPeriodEnum]


@app.delete("/delete_universes")
async def delete_universes(body: db.DeleteUniverseRequestBody):
    """
    Delete a set of universes based on the list of universe_ids provided.
    """
    db.delete_universes(body)
    return {"message": "Universes deleted successfully", "deleted_ids": body.universe_ids}