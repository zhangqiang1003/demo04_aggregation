from typing import List, Optional

from pydantic import BaseModel


class AggregatorRequest(BaseModel):
    query: str
    focusModes: List[str]
    options: dict = {}


class SourceResult(BaseModel):
    source: str
    items: List[dict]


class AggregatorResponse(BaseModel):
    query: str
    aggregatedResults: List[SourceResult]
    summary: Optional[str] = None
