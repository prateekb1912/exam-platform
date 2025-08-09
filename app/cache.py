import os
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = 6379

client = Redis(host=REDIS_HOST, port= REDIS_PORT)

def set_key(key, value):
    client.set(key, value)

def get_key(key):
    return client.get(key)

def cache_total_ranks(test_id, aggregated_scores):
    pipe = client.pipeline()
    for doc in aggregated_scores:
        uid = str(doc["_id"])
        total_score = doc["total_score"]
        pipe.zadd(f"leaderboard:{test_id}", {uid: total_score})
    pipe.execute()

def get_user_rank_from_cache(test_id, user_id):
    total_users = client.zcard(f"leaderboard:{test_id}")
    rank = client.zrevrank(f"leaderboard:{test_id}", user_id)
    score = client.zscore(f"leaderboard:{test_id}", user_id)

    if rank is None or score is None:
        return None

    percentile = 100.0 * (1 - rank / total_users)

    return {
        "rank": rank + 1,
        "score": score,
        "percentile": percentile
    }