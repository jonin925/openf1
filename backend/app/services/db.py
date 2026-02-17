import asyncpg
from app.core.config import settings

async def get_pool():
    return await asyncpg.create_pool(
        dsn=settings.POSTGRES_DSN,
        min_size=1,
        max_size=5,
    )
