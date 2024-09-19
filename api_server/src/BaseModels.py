from pydantic import BaseModel
from typing import List

# Define a Pydantic model for the request body
class UniverseRequestBody(BaseModel):
    name: str
    tickers: List[str]
    date_range: str
    measurement_period: int