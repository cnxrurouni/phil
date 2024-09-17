from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_tickers, post_create_universe, UniverseRequestBody


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
    tickers = get_tickers()
    return {"tickers": tickers}


@app.post("/create_universe")
async def create_universe(body: UniverseRequestBody):
    universe = post_create_universe(body)
    return {"universe": universe}