from pydantic import BaseModel
from typing import List

# Define a Pydantic model for the request body
class CreateUniverseRequestBody(BaseModel):
    name: str
    tickers: List[str]
    date_range: str
    measurement_period: int


class EditUniverseRequestBody(CreateUniverseRequestBody):
    pass


class DeleteUniverseRequestBody(BaseModel):
    universe_ids: List[int]