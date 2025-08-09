from bson import ObjectId
from collections import defaultdict

from app.db import submissionCollection
from app.td import serialize_tdigest, deserialize_tdigest, TDigest
from app.cache import set_key, get_key

async def calculate_total_scores(test_id):
    pipeline = [
        {"$match": {"test_id": ObjectId(test_id)}},
        {
            "$group": {
                "_id": "$user_id",
                "total_score": {"$sum": "$marks"},
                "subjects": {
                    "$push": {"subject": "$subject", "score": "$marks"}
                }
            }
        },
        {"$sort": {"total_score": -1}}
    ]

    return [doc async for doc in submissionCollection.aggregate(pipeline)]

async def calculate_subject_percentiles(test_id, aggregated_scores):
    for doc in aggregated_scores:
        subjects = defaultdict(int)
        for s in doc["subjects"]:
            subjects[s["subject"]] += s["score"]
        doc["subjects"] = dict(subjects)

    subject_digests = defaultdict(TDigest)
    for doc in aggregated_scores:
        for sub, sc in doc["subjects"].items():
            subject_digests[sub].update(sc)

    for sub, td in subject_digests.items():
        set_key(f"tdigest:{test_id}:{sub}", serialize_tdigest(td))
    
    for doc in aggregated_scores:
        doc["subject_percentiles"] = {}
        for sub, sc in doc["subjects"].items():
            td_data = get_key(f"tdigest:{test_id}:{sub}")
            if td_data:
                td = deserialize_tdigest(td_data.decode())
                percentile = 100.0 * (1 - td.rank(sc))
                doc["subject_percentiles"][sub] = percentile

    return aggregated_scores