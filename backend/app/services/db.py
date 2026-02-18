import os
import asyncpg
import asyncio

async def get_pool():
    return await asyncpg.create_pool(
        dsn=os.getenv(
            "POSTGRES_DSN",
            "postgresql://f1user:strongpassword@localhost:5433/f1db"
        ),
        min_size=1,
        max_size=5
    )
