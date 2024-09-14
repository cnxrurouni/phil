from pydantic import BaseModel

# Define a Pydantic model for the request body
class UniverseRequestBody(BaseModel):
    name: str
    tickers: list = None