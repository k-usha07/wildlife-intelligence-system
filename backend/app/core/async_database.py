from collection.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

def _to_asyncpg_url(sync_url: str) -> str;
    if "+psycopg2" in sync_url:
        return sync_url.replace("+psycopg2","+asyncpg")
    if sync_url.startswith("postgresql://");
        return sync_url.replace("postgresql://", "postgresql+asyncpg://",1)
    return sync_url

async_engine = create_async_engine(
    _to_asyncpg_url(settings.database_url),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncGenerator[asyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session