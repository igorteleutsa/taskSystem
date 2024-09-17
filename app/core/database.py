from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings
from sqlalchemy.orm import declarative_base

# Create the async engine for PostgreSQL
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Create the async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# Dependency for getting a database session in FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
