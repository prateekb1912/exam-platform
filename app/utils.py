from bson import ObjectId
from collections import defaultdict

from app.db import submissionCollection

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


async def calculate_ranks(test_id, aggregated_scores):
    # aggregated_scores = await calculate_total_scores(test_id)

    total_users = len(aggregated_scores)
    rank = 1
    prev_score = None
    results = []

    for idx, doc in enumerate(aggregated_scores):
        user_id = doc["_id"]
        score = doc["total_score"]

        if prev_score is None or score < prev_score:
            rank = idx + 1
        prev_score = score

        percentile = 100.0 * (1 - (rank - 1) / total_users)

        results.append({
            "user_id": str(user_id),
            "score": score,
            "rank": rank,
            "percentile": percentile
        })
    

    return results

async def calculate_subject_percentiles(test_id, aggregated_scores):
    for doc in aggregated_scores:
        subjects = defaultdict(int)
        for s in doc["subjects"]:
            subjects[s["subject"]] += s["score"]
        doc["subjects"] = dict(subjects)

    subject_score_lists = defaultdict(list)
    for doc in aggregated_scores:
        for sub, sc in doc["subjects"].items():
            subject_score_lists[sub].append(sc)

    subject_percentile_map = {}
    for sub, scores in subject_score_lists.items():
        scores.sort(reverse=True)
        total = len(scores)
        score_to_percentile = {}
        rank = 1
        prev_score = None
        for idx, score in enumerate(scores):
            if prev_score is None or score < prev_score:
                rank = idx + 1
            prev_score = score
            score_to_percentile[score] = 100.0 * (1 - (rank - 1) / total)
        subject_percentile_map[sub] = score_to_percentile

    for doc in aggregated_scores:
        doc["subject_percentiles"] = {
            sub: subject_percentile_map[sub][sc]
            for sub, sc in doc["subjects"].items()
        }