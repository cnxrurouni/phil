from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import database as db
from models import MeasurementPeriodEnum
from typing import List
from datetime import date


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

# sample query: http://your-domain.com/get_short_interest?ticker=AAPL&start_date=2024-01-01&end_date=2024-02-01
@app.get("/get_short_interest") #, response_model=list[db.ShortInterestResponse])
async def get_short_interest(
    tickers: str,
    start_date: date = Query(..., description="Start of date range"),
    end_date: date = Query(..., description="End of date range"),
):
    ticker_list = tickers.split(',')
    short_interest = db.get_short_interest_for_tickers(ticker_list, start_date, end_date)
    return {'short_interest': short_interest}