from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.router import router
from fastapi.responses import JSONResponse
from fastapi import HTTPException


@asynccontextmanager
async def life_span(app: FastAPI):
    print("🚀 Starting up...")
    try:
        await init_db()
        print("✅ Startup complete!")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        # Don't raise - let the app start anyway
        # This allows you to see error messages
    yield
    print("🛑 Shutting down...")


app = FastAPI(
    title="Country Currency & Exchange API",
    description="RESTful API for country data with exchange rates",
    lifespan=life_span,
)
app.include_router(router)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    import uvicorn
    import os
    from src import app 

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)