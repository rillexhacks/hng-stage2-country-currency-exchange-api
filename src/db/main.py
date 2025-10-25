from sqlmodel import SQLModel, create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

# Create async engine properly
engine = create_async_engine(
    config.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

# Create async session maker
async_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Initialize the database
async def init_db():
    try:
        print("🔄 Connecting to database...")
        async with asyncio.timeout(30):  # 30 second timeout
            async with engine.begin() as conn:
                print("✅ Connected! Creating tables...")
                await conn.run_sync(SQLModel.metadata.create_all)
                print("✅ Database initialized successfully!")
    except asyncio.TimeoutError:
        print("❌ Database connection timeout!")
        raise
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise



# Dependency to get DB session
async def get_session():
    async with async_session_maker() as session:
        yield session
