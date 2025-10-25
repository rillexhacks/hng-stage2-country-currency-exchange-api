# Country Currency & Exchange API

A RESTful API that fetches country data from external APIs, stores it in a MySQL database, and provides CRUD operations with currency exchange rate calculations.

## 🌐 Live Demo

The API is deployed and accessible at:
**https://ectotrophic-thromboplastically-langston.ngrok-free.dev/**

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Database Configuration](#database-configuration)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Usage Examples](#api-usage-examples)
- [Deployment](#deployment)
- [Error Handling](#error-handling)
- [Contributing](#contributing)

## ✨ Features

- **Data Fetching**: Automatically fetches country data from RestCountries API
- **Exchange Rates**: Integrates with Open Exchange Rates API for real-time currency data
- **GDP Calculation**: Computes estimated GDP using population and exchange rates
- **Database Caching**: Stores and caches data in MySQL database
- **CRUD Operations**: Full Create, Read, Update, Delete functionality
- **Filtering & Sorting**: Support for region and currency filtering, GDP sorting
- **Image Generation**: Creates summary images with country statistics
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Validation**: Input validation with detailed error messages

## 🛠 Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: MySQL
- **ORM**: SQLModel (built on SQLAlchemy)
- **Image Processing**: Pillow (PIL)
- **HTTP Client**: httpx
- **Validation**: Pydantic
- **Database**: MySQL (Local/Remote)
- **Deployment**: ngrok tunnel

## 📁 Project Structure

```
stage2_country_currency_exchange_api/
├── src/
│   ├── __init__.py           # FastAPI app initialization
│   ├── config.py             # Configuration settings
│   ├── models.py             # SQLModel database models
│   ├── router.py             # API route handlers
│   ├── schemas.py            # Pydantic models for validation
│   ├── services.py           # Business logic and external API calls
│   ├── image_generator.py    # Image generation utilities
│   └── db/
│       ├── __init__.py
│       └── main.py           # Database connection and session management
├── cache/                    # Directory for generated images
├── .env                      # Environment variables
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔗 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/countries/refresh` | Fetch and cache all countries with exchange rates |
| `GET` | `/countries` | Get all countries (supports filtering and sorting) |
| `GET` | `/countries/{name}` | Get a specific country by name |
| `DELETE` | `/countries/{name}` | Delete a country record |
| `GET` | `/status` | Get total countries count and last refresh timestamp |
| `GET` | `/countries/image` | Serve the generated summary image |

### Query Parameters

#### GET /countries
- `region`: Filter by region (e.g., `?region=Africa`)
- `currency`: Filter by currency code (e.g., `?currency=NGN`)
- `sort`: Sort results (e.g., `?sort=gdp_desc`)

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL database
- pip (Python package manager)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stage2_country_currency_exchange_api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create cache directory**
   ```bash
   mkdir cache
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## 🗄 Database Configuration

### Local MySQL Setup

1. **Install MySQL** (if not already installed)
2. **Create database**
   ```sql
   CREATE DATABASE country_db;
   ```

3. **Create user and grant permissions**
   ```sql
   CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON country_db.* TO 'your_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Remote MySQL Setup

For production or remote MySQL hosting:

1. **Set up your MySQL host** (can be any cloud provider)
2. **Configure connection details**
3. **Update environment variables** with your database credentials
4. **Ensure proper SSL/security settings**

## 🔧 Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=mysql+asyncmy://username:password@host:port/database_name

# For Remote MySQL (Production)
# DATABASE_URL=mysql+asyncmy://username:password@host:port/database_name?ssl=require

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000

# External APIs
COUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_RATE_API_URL=https://open.er-api.com/v6/latest/USD

# Cache Configuration
CACHE_DIR=cache

# Timeout Configuration
TIMEOUT=30
```

## ▶️ Running the Application

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run with uvicorn
uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

### Running with ngrok

To expose your local development server to the internet:

1. **Start your FastAPI application**:
   ```bash
   uvicorn src:app --reload --host 0.0.0.0 --port 8000
   ```

2. **In another terminal, start ngrok**:
   ```bash
   ngrok http 8000
   ```

3. **Access your API** using the ngrok URL provided

The API will be available at `http://localhost:8000` locally and via your ngrok URL publicly.

## 📖 API Usage Examples

### 1. Refresh Countries Data

```bash
curl -X POST "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries/refresh"
```

**Response:**
```json
{
  "message": "Countries data refreshed successfully",
  "total_countries": 250,
  "updated": 0,
  "inserted": 250,
  "last_refreshed_at": "2025-10-25T19:30:00Z"
}
```

### 2. Get All Countries

```bash
curl "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries"
```

### 3. Filter by Region

```bash
curl "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries?region=Africa"
```

### 4. Filter by Currency

```bash
curl "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries?currency=NGN"
```

### 5. Sort by GDP (Descending)

```bash
curl "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries?sort=gdp_desc"
```

### 6. Get Specific Country

```bash
curl "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries/Nigeria"
```

### 7. Delete Country

```bash
curl -X DELETE "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries/Nigeria"
```

### 8. Get Status

```bash
curl "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/status"
```

**Response:**
```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-25T19:30:00Z"
}
```

### 9. Get Summary Image

```bash
curl "https://ectotrophic-thromboplastically-langston.ngrok-free.dev/countries/image"
```

## 🌍 Sample API Responses

### GET /countries?region=Africa

```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1600.23,
    "estimated_gdp": 25767448125.2,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-25T19:30:00Z"
  },
  {
    "id": 2,
    "name": "Ghana",
    "capital": "Accra",
    "region": "Africa",
    "population": 31072940,
    "currency_code": "GHS",
    "exchange_rate": 15.34,
    "estimated_gdp": 3029834520.6,
    "flag_url": "https://flagcdn.com/gh.svg",
    "last_refreshed_at": "2025-10-25T19:30:00Z"
  }
]
```

## 🚀 Deployment

### ngrok Deployment

This project is exposed via ngrok tunnel:

1. **Install ngrok**: Download from https://ngrok.com/
2. **Run your application locally**:
   ```bash
   uvicorn src:app --host 0.0.0.0 --port 8000
   ```
3. **Start ngrok tunnel**:
   ```bash
   ngrok http 8000
   ```
4. **Use the provided URL**: ngrok will give you a public URL to access your local API

### Deployment Checklist

- ✅ Database configured (MySQL)
- ✅ Environment variables set
- ✅ Dependencies listed in requirements.txt
- ✅ Proper start command configured
- ✅ ngrok tunnel configured
- ✅ Error handling implemented
- ✅ Logging configured

## ❌ Error Handling

The API implements comprehensive error handling:

### HTTP Status Codes

- `200 OK`: Successful requests
- `400 Bad Request`: Validation errors
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server errors
- `503 Service Unavailable`: External API failures

### Error Response Format

```json
{
  "error": "Error type",
  "details": "Detailed error message or validation errors"
}
```

### Examples

**Validation Error (400):**
```json
{
  "error": "Validation failed",
  "details": {
    "currency_code": "is required"
  }
}
```

**Not Found (404):**
```json
{
  "error": "Country not found"
}
```

**Service Unavailable (503):**
```json
{
  "error": "External data source unavailable",
  "details": "Could not fetch data from Countries API"
}
```

## 🔄 Data Flow

1. **POST /countries/refresh**:
   - Fetch countries from RestCountries API
   - Extract currency codes
   - Fetch exchange rates from Open Exchange Rates API
   - Calculate estimated GDP
   - Store/update in database
   - Generate summary image

2. **Currency Handling**:
   - Multiple currencies: Use first currency code
   - Empty currencies: Set fields to null, estimated_gdp to 0
   - Missing exchange rate: Set exchange_rate and estimated_gdp to null

3. **Update Logic**:
   - Match countries by name (case-insensitive)
   - Update existing records or insert new ones
   - Recalculate estimated_gdp with fresh random multiplier

## 🧪 Testing

Test the API endpoints using the live deployment:

```bash
# Base URL
BASE_URL="https://ectotrophic-thromboplastically-langston.ngrok-free.dev"

# Test status endpoint
curl "$BASE_URL/status"

# Test refresh (this might take a few seconds)
curl -X POST "$BASE_URL/countries/refresh"

# Test filtering
curl "$BASE_URL/countries?region=Africa&limit=5"
```

## 📝 Implementation Notes

### Key Features Implemented

✅ **All Required Endpoints**: POST /countries/refresh, GET /countries, GET /countries/:name, DELETE /countries/:name, GET /status, GET /countries/image

✅ **External API Integration**: RestCountries API and Open Exchange Rates API

✅ **Database Operations**: MySQL with SQLModel ORM

✅ **Currency Handling**: Proper handling of multiple currencies, missing currencies, and missing exchange rates

✅ **GDP Calculation**: estimated_gdp = population × random(1000–2000) ÷ exchange_rate

✅ **Filtering & Sorting**: Region, currency filtering and GDP sorting

✅ **Image Generation**: Summary images with country statistics

✅ **Error Handling**: Comprehensive error responses with proper HTTP status codes

✅ **Validation**: Input validation with detailed error messages

✅ **Update Logic**: Case-insensitive country matching with update/insert logic

### Technical Decisions

- **FastAPI**: Chosen for automatic API documentation and async support
- **SQLModel**: Provides robust ORM capabilities with type safety
- **Pydantic**: Ensures data validation and serialization
- **MySQL**: Reliable relational database for structured country data
- **ngrok**: Secure tunneling service for exposing local development

### Database Schema

The [`Country` model](src/models.py:6) includes all required fields:

```python
class Country(SQLModel, table=True):
    id: int (Primary Key)
    name: str (Required, Unique)
    capital: Optional[str]
    region: Optional[str]
    population: int (Required)
    currency_code: Optional[str]
    exchange_rate: Optional[float]
    estimated_gdp: Optional[float]
    flag_url: Optional[str]
    last_refreshed_at: datetime (Auto-updated)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of the HNG internship program.

---

**Live API**: https://ectotrophic-thromboplastically-langston.ngrok-free.dev/

For any issues or questions, please check the API documentation at the `/docs` endpoint of the live URL.