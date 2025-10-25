from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CountryResponse(BaseModel):
    id: int
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: datetime
    
    class Config:
        from_attributes = True

class StatusResponse(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[datetime] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[dict] = None

class RefreshResponse(BaseModel):
    message: str
    total_countries: int
    updated: int
    inserted: int
    last_refreshed_at: datetime