from arq import ArqRedis, create_pool
from app.core.config import settings
from app.worker import get_redis_settings

_pool: ArqRedis | None=None

async def init_queue() -> None:
    global _pool
    _pool = await create_pool(get_redis_settings())

async def close_queue() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

def get_queue() -> ArqRedis:
    if _pool is None:
        raise RuntimeError("Queue not initialised - is init_queue() called in app startup?")
    return _pool

async def enqueue_media_processing(media_asset_id: str) -> None:
    await get_queue().enqueue_job("process_media_asset", media_asset_id=media_asset_id)