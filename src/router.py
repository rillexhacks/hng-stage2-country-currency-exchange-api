from fastapi import APIRouter, HTTPException, FastAPI, Depends
from fastapi.params import Query
from fastapi.responses import FileResponse
from src.schemas import RefreshResponse, StatusResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.services import CountryService
from typing import Optional
import os
from src.config import config





router = APIRouter()


@router.get("/", response_model=dict, tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Country Currency & Exchange API",
        "endpoints": {
            "POST /countries/refresh": "Refresh country data from external APIs",
            "GET /countries": "Get all countries (filters: ?region=Africa&currency=NGN&sort=gdp_desc)",
            "GET /countries/{name}": "Get a specific country by name",
            "DELETE /countries/{name}": "Delete a country by name",
            "GET /status": "Get API status",
            "GET /countries/image": "Get summary image",
        },
    }

@router.post("/countries/refresh-test", tags=["Countries"])
async def refresh_countries_test():
    """Test endpoint without database"""
    service = CountryService()
    
    try:
        # Just fetch and return the data without saving to DB
        countries_data = await service.fetch_countries_data()
        exchange_rates = await service.fetch_exchange_rates()
        
        return {
            "message": "Data fetched successfully (not saved to DB)",
            "total_countries": len(countries_data),
            "sample_country": countries_data[0] if countries_data else None,
            "sample_rates": dict(list(exchange_rates.items())[:5])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#  Endpoint to refresh countries data
@router.post("/countries/refresh", response_model=RefreshResponse, tags=["Countries"])
async def refresh_countries(db: AsyncSession = Depends(get_session)):
    """Refresh countries data by delegating to CountryService instance."""
    service = CountryService()

    try:
        total_countries, updated, inserted = await service.refresh_countries(db)

        # Get latest refresh timestamp
        status = await service.get_status(db)

        return RefreshResponse(
            message="Countries data refreshed successfully",
            total_countries=total_countries,
            updated=updated,
            inserted=inserted,
            last_refreshed_at=(
                status.get("last_refreshed_at") if isinstance(status, dict) else None
            ),
        )

    except Exception as e:
        error_message = str(e)

        # Check if it's an external API error
        if "Could not fetch data" in error_message or "timed out" in error_message:
            # Determine which API failed
            api_name = (
                "Countries API"
                if "Countries API" in error_message
                else "Exchange Rate API"
            )

            raise HTTPException(
                status_code=503,
                detail={
                    "error": "External data source unavailable",
                    "details": f"Could not fetch data from {api_name}",
                },
            )

        # Generic server error
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/countries", response_model=list[dict], tags=["Countries"])
async def get_countries(
    region: Optional[str] = Query(
        None, description="Filter by region (e.g., Africa, Europe)"
    ),
    currency: Optional[str] = Query(
        None, description="Filter by currency code (e.g., NGN, USD)"
    ),
    sort: Optional[str] = Query(
        None,
        description="Sort by: gdp_desc, gdp_asc, population_desc, population_asc, name_asc, name_desc",
    ),
    db: AsyncSession = Depends(get_session),
):
    ser = CountryService()
    countries = await ser.get_countries(db, region, currency, sort)

    # Convert each SQLAlchemy model instance to dict
    countries_list = [country.__dict__ for country in countries]
    # Remove SQLAlchemy internal key
    for c in countries_list:
        c.pop("_sa_instance_state", None)

    return countries_list


@router.get("/countries/image", tags=["Image"])
async def get_summary_image():
    ser = CountryService()
    await ser.generate_summary_image_if_missing()
    cache_dir = config.CACHE_DIR
    image_path = os.path.join(cache_dir, 'summary.png')
    
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail="Summary image not found"
        )
    
    return FileResponse(
        image_path,
        media_type="image/png",
        filename="summary.png"
    )


@router.get("/countries/{name}", response_model=dict, tags=["Countries"])
async def get_country_by_name(
    name: str,
    db: AsyncSession = Depends(get_session)
):
    ser = CountryService()
    country = await ser.get_country_by_name(db, name)  # async version

    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )

    # Convert to dict and remove SQLAlchemy internal key
    country_dict = country.__dict__.copy()
    country_dict.pop("_sa_instance_state", None)

    return country_dict


@router.delete("/countries/{name}", tags=["Countries"])
async def delete_country(
    name: str,
    db: AsyncSession = Depends(get_session)
):
    ser = CountryService()
    deleted = await ser.delete_country_by_name(db, name) 

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Country not found"
        )

    return {"message": f"Country '{name}' deleted successfully"}


@router.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status( db: AsyncSession = Depends(get_session)):
    ser = CountryService()
    status = await ser.get_status(db)
    return StatusResponse(**status)


