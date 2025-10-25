from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.router import router 
from fastapi.responses import  JSONResponse
from fastapi import HTTPException


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down...")


app = FastAPI(
    title="Country Currency & Exchange API",
    description="RESTful API for country data with exchange rates",
    lifespan=life_span,
)
app.include_router(router)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
