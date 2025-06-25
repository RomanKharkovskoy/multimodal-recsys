from pydantic import BaseModel
from datetime import datetime


class BusinessCreate(BaseModel):
    name: str
    industry: str
    contact_email: str


class BusinessUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    contact_email: str | None = None


class BusinessResponse(BaseModel):
    id: int
    name: str
    industry: str
    contact_email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainRequest(BaseModel):
    n_samples: int = 50
    use_tabular: bool = True
    use_text: bool = True
    n_neighbors: int = 6


class RecommendationResponse(BaseModel):
    query_index: int
    product_name: str
    recommendations: list[dict]
