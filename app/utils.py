import json

from bson import ObjectId
from collections import defaultdict

from app.db import submissionCollection
from tdigest import TDigest
from app.cache import set_key, get_key

"""
Sample total_scores document:

{
  _id: ObjectId('689783d79cf4803f0a8b14c4'),
  total_score: 88,
  subjects: [
    {
      subject: 'Math',
      score: 88
    }
  ]
}
"""

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
    td_total = TDigest()
    scores = []

    for doc in aggregated_scores:
        total = doc['total_score']
        scores.append(total)
        td_total.update(total)

        subjects = defaultdict(int)
        for s in doc["subjects"]:
            subjects[s["subject"]] += s["score"]
        doc["subjects"] = dict(subjects)

    subject_digests = defaultdict(TDigest)
    for doc in aggregated_scores:
        for sub, sc in doc["subjects"].items():
            subject_digests[sub].update(sc)

    set_key(f"tdigest:{test_id}:total", td_total.to_dict())
    set_key(f"tdigest:{test_id}:N_total", len(scores))
    for sub, td in subject_digests.items():
        set_key(f"tdigest:{test_id}:{sub}", td.to_dict())
    
    for doc in aggregated_scores:
        doc["subject_percentiles"] = {}
        for sub, sc in doc["subjects"].items():
            td_data = get_key(f"tdigest:{test_id}:{sub}")
            if td_data:
                td = TDigest.from_json(get_key(f"td:{test_id}:{sub}").decode())
                percentile = 100.0 * (1 - td.rank(sc))
                doc["subject_percentiles"][sub] = percentile

    return aggregated_scores

async def predict_ranks_percentiles(test_id, mock_total, mock_subject_scores=[]):
    td_total = TDigest.from_json(get_key(f"tdigest:{test_id}:total").decode())
    N_total = int(get_key(f"tdigest:{test_id}:N_total"))

    frac_less = td_total.rank(mock_total) 
    percentile = 100.0 * (1 - frac_less)
    rank = max(1, int(round((1 - frac_less) * N_total)))

    results = {
        "predicted_total_rank": rank,
        "predicted_total_percentile": percentile
    }

    if mock_subject_scores:
        results["subjects"] = {}
        for sub, sc in mock_subject_scores.items():
            td_sub = TDigest.from_json(get_key(f"tdigest:{test_id}:{sub}").decode())
            frac_less_sub = td_sub.rank(sc)
            pct_sub = 100.0 * (1 - frac_less_sub)
            results["subjects"][sub] = pct_sub

    return results