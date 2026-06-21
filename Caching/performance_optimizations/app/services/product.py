import json
import logging
import random
from app.schemas.product import ProductCreate, ProductPublic
from fastapi import HTTPException

logger = logging.getLogger("uvicorn.error")


async def get_product_catalog(
    product_id: str,
    db,
    redis,
    execute_heavy_db_query: callable,
    use_cache: bool = True,
    use_lock: bool = False,
):
    cache_key = f"cache:product:{product_id}"
    lock_key = f"lock:product:{product_id}"

    if not use_cache:
        logger.warning(
            f"🚫 Cache disabled. Reading directly from Postgres for key: {cache_key}"
        )
        db_data = await execute_heavy_db_query(db, product_id)
        if not db_data:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductPublic(**db_data.model_dump(mode="json"))

    # 1. Look up data inside cache layer
    cached_data = await redis.get(cache_key)
    if cached_data:
        return ProductPublic(**json.loads(cached_data))

    # ---- CRITICAL PATH LINE: Scenario Toggle ----

    # SCENARIO A: The Unprotected Cache Stampede (Default)
    if not use_lock:
        logger.warning(
            f"💥 Stampede Hit! Directing query to Postgres for key: {cache_key}"
        )
        db_data = await execute_heavy_db_query(db, product_id)
        if not db_data:
            raise HTTPException(status_code=404, detail="Product not found")

        db_data_dict = db_data.model_dump(mode="json")
        # Write back to cache with 60s TTL
        await redis.setex(cache_key, 3600, json.dumps(db_data_dict))
        return ProductPublic(**db_data_dict)

    # SCENARIO B: Thundering Herd Mitigation via Distributed Mutex Guard
    else:
        # Request an atomic mutex with 5s timeout to prevent system deadlocking
        async with redis.lock(lock_key, timeout=5, blocking_timeout=4) as lock:
            # Double-Check Loop Pattern
            cached_data = await redis.get(cache_key)
            if cached_data:
                logger.info("🛡️ Mutex Safeguard: Cache Hit verified on inner check.")
                return ProductCreate(**json.loads(cached_data))

            logger.warning(
                f"🔑 Mutex Acquired. Exactly ONE worker querying Postgres for: {cache_key}"
            )
            db_data = await execute_heavy_db_query(db, product_id)
            if not db_data:
                raise HTTPException(status_code=404, detail="Product not found")

            db_data_dict = db_data.model_dump(mode="json")
            # Apply a 60 second base TTL with a 1-5 second randomized jitter
            # to prevent all keys from structurally expiring at the same time.
            ttl_jitter = 3600 + random.randint(1, 5)
            await redis.setex(cache_key, ttl_jitter, json.dumps(db_data_dict))
            return ProductPublic(**db_data_dict)
