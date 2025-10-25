import httpx
import random
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func, select
from src.models import Country
from datetime import datetime
from src.config import config
from typing import Optional, Tuple, List
from src.image_generator import generate_summary_image
import os


class CountryService:

    def __init__(self):
        self.countries_api_url = config.COUNTRIES_API_URL
        self.exchange_rate_api_url = config.EXCHANGE_RATE_API_URL
        self.cache_dir = config.CACHE_DIR
        self.timeout = config.TIMEOUT  # type: float

    async def fetch_countries_data(self) -> list:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.countries_api_url)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise Exception("Countries API request timed out")
        except httpx.HTTPError as e:
            raise Exception(f"Could not fetch data from Countries API: {str(e)}")

    async def fetch_exchange_rates(self) -> dict:
        """Fetch exchange rates from external API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.exchange_rate_api_url)
                response.raise_for_status()
                data = response.json()
                return data.get("rates", {})
        except httpx.TimeoutException:
            raise Exception("Exchange Rate API request timed out")
        except httpx.HTTPError as e:
            raise Exception(f"Could not fetch data from Exchange Rate API: {str(e)}")

    def extract_currency_code(self, currencies: list) -> Optional[str]:
        if not currencies or len(currencies) == 0:
            return None

        # Get first currency
        first_currency = currencies[0]

        # Currency can be in different formats, extract code
        if isinstance(first_currency, dict):
            return first_currency.get("code")
        elif isinstance(first_currency, str):
            return first_currency

        return None

    def calculate_estimated_gdp(
        self, population: int, exchange_rate: Optional[float]
    ) -> Optional[float]:
        """Calculate estimated GDP based on population and exchange rate"""
        if exchange_rate is None or exchange_rate == 0:
            return None

        # Generate random multiplier between 1000 and 2000
        multiplier = random.uniform(1000, 2000)

        # Calculate: population × multiplier ÷ exchange_rate
        estimated_gdp = (population * multiplier) / exchange_rate

        return estimated_gdp

    def process_country_data(self, country_data: dict, exchange_rates: dict) -> dict:
        """Process a single country's data"""
        name = country_data.get("name")
        capital = country_data.get("capital")
        region = country_data.get("region")
        population = country_data.get("population", 0)
        flag_url = country_data.get("flag")
        currencies = country_data.get("currencies", [])

        # Extract currency code
        currency_code = self.extract_currency_code(currencies)

        # Handle cases based on currency availability
        if currency_code is None:
            # No currency - set everything to null/0
            exchange_rate = None
            estimated_gdp = 0.0
        else:
            # Get exchange rate for this currency
            exchange_rate = exchange_rates.get(currency_code)

            if exchange_rate is None:
                # Currency code not found in exchange rates
                estimated_gdp = None
            else:
                # Calculate GDP
                estimated_gdp = self.calculate_estimated_gdp(population, exchange_rate)

        return {
            "name": name,
            "capital": capital,
            "region": region,
            "population": population,
            "currency_code": currency_code,
            
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag_url,
        }

    #
    async def refresh_countries(self, db: AsyncSession) -> Tuple[int, int, int]:
        # Fetch data from external APIs
        countries_data = await self.fetch_countries_data()
        exchange_rates = await self.fetch_exchange_rates()

        updated_count = 0
        inserted_count = 0

        # Process each country
        for country_data in countries_data:
            try:
                # Extract and process country data
                processed_data = self.process_country_data(country_data, exchange_rates)

                # Extract currency code using your existing method
                currency_code = self.extract_currency_code(
                    country_data.get("currencies", [])
                )
                processed_data["currency_code"] = currency_code

                # Get the exchange rate for this currency
                if currency_code and exchange_rates.get(currency_code):
                    processed_data["exchange_rate"] = exchange_rates[currency_code]
                else:
                    processed_data["exchange_rate"] = None

                # Validate required fields
                if not processed_data["name"] or processed_data["population"] is None:
                    continue

                # Check if country exists (case-insensitive) using async query
                q = select(Country).where(
                    func.lower(Country.name) == func.lower(processed_data["name"])
                )
                result = await db.exec(q)
                existing_country = result.scalars().first()

                if existing_country:
                    # Update existing country
                    for key, value in processed_data.items():
                        setattr(existing_country, key, value)
                    existing_country.last_refreshed_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Insert new country
                    new_country = Country(**processed_data)
                    db.add(new_country)
                    inserted_count += 1

            except Exception as e:
                print(f"Error processing country: {str(e)}")
                continue

        # Commit all changes
        await db.commit()

        # Generate summary image
        await self.generate_summary(db)

        # Get total countries (async)
        total_q = select(func.count()).select_from(Country)
        total_result = await db.exec(total_q)
        total_countries = total_result.scalar_one() if total_result is not None else 0

        return total_countries, updated_count, inserted_count

    # Generate summary image
    async def generate_summary(self, db: AsyncSession):
        """Generate summary image with top countries"""
        # Get total countries
        total_q = select(func.count()).select_from(Country)
        total_result = await db.exec(total_q)
        total_countries = total_result.scalar_one() if total_result is not None else 0

        # Get top 5 countries by estimated GDP
        top_q = (
            select(Country.name, Country.estimated_gdp)
            .where(Country.estimated_gdp.isnot(None))
            .order_by(Country.estimated_gdp.desc())
            .limit(5)
        )

        top_result = await db.exec(top_q)
        # Convert rows to list of tuples (name, gdp)
        top_countries_rows = top_result.all()
        top_countries = [(r[0], r[1]) for r in top_countries_rows]

        # Generate image
        generate_summary_image(total_countries, top_countries, self.cache_dir)

    async def get_status(self, db: AsyncSession) -> dict:
        """Return status info such as last_refreshed_at."""
        q = select(func.max(Country.last_refreshed_at))
        result = await db.exec(q)
        last_refreshed = result.scalar()
        return {"last_refreshed_at": last_refreshed}

    async def get_countries(
        self,
        db: AsyncSession,
        region: Optional[str] = None,
        currency: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[Country]:
        """Return list of countries applying filters and sorting (async)."""

        statement = select(Country)

        # Apply filters
        if region:
            statement = statement.where(func.lower(Country.region) == func.lower(region))

        if currency:
            statement = statement.where(func.lower(Country.currency_code) == func.lower(currency))

        # Apply sorting
        if sort:
            sort_lower = sort.lower()
            if sort_lower == "gdp_desc":
                statement = statement.order_by(Country.estimated_gdp.desc().nullslast())
            elif sort_lower == "gdp_asc":
                statement = statement.order_by(Country.estimated_gdp.asc().nullsfirst())
            elif sort_lower == "population_desc":
                statement = statement.order_by(Country.population.desc())
            elif sort_lower == "population_asc":
                statement = statement.order_by(Country.population.asc())
            elif sort_lower == "name_asc":
                statement = statement.order_by(Country.name.asc())
            elif sort_lower == "name_desc":
                statement = statement.order_by(Country.name.desc())
        else:
            # Default sort by name ascending
            statement = statement.order_by(Country.name.asc())

        result = await db.exec(statement)
        countries = result.scalars().all()
        return countries


    async def get_country_by_name(self, db: AsyncSession, country_name: str) -> Optional[Country]:
        """Get a single country by name (case-insensitive)"""
        q = select(Country).where(func.lower(Country.name) == func.lower(country_name))
        result = await db.exec(q)
        country = result.scalars().first()
        return country
    

    async def delete_country_by_name(self, db: AsyncSession, country_name: str) -> bool:
        # Use async get
        country = await self.get_country_by_name(db, country_name)
        
        if country:
            await db.delete(country)      # await delete
            await db.commit()             # await commit
            return True
    
        return False
    
    async def get_status(self, db: AsyncSession) -> dict:
        """Get database status asynchronously."""

        # Total countries
        statement = select(func.count()).select_from(Country)
        total_result = await db.exec(statement)
        total_countries = total_result.scalar_one()  # always returns a number

        # Latest refresh timestamp
        latest_q = select(func.max(Country.last_refreshed_at))
        latest_result = await db.exec(latest_q)
        latest_refresh = latest_result.scalar_one_or_none()  # could be None

        return {
            "total_countries": total_countries,
            "last_refreshed_at": latest_refresh
        }
    


    async def generate_summary_image_if_missing(self, db: AsyncSession):
        if not os.path.exists(config.CACHE_DIR):
            os.makedirs(config.CACHE_DIR)
        image_path = os.path.join(config.CACHE_DIR, "summary.png")
        if not os.path.exists(image_path):
            # Call your image generation function here
          await self.generate_summary(db)