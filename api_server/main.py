from fastapi import FastAPI
import src.database as db

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI with PostgreSQL!"}

@app.get("/tickers")
async def read_tickers():
    tickers = db.get_tickers()
    return {"tickers": tickers}