from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Country(SQLModel, table=True):
    __tablename__ = "countries"

    # Auto-generated ID (required, but auto-incremented)
    id: int = Field(default=None, primary_key=True, index=True)

    # Required fields
    name: str = Field(index=True, unique=True, nullable=False, max_length=255)
    population: int = Field(nullable=False)
    currency_code: Optional[str] = Field(default=None, max_length=10)

    # Optional fields
    capital: Optional[str] = Field(default=None, max_length=255)
    region: Optional[str] = Field(default=None, max_length=100)
    flag_url: Optional[str] = Field(default=None, max_length=500)
   
    

    # Computed / derived fields
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None

    # Auto timestamp
    last_refreshed_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    def __repr__(self):
        return f"<Country(id={self.id}, name={self.name}, currency={self.currency_code})>"
