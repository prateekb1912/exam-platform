from bson import ObjectId
from fastapi import APIRouter, status

from app.schemas import Test
from app.db import testCollection
from app.utils import calculate_total_scores, calculate_subject_percentiles, predict_ranks_percentiles
from app.cache import cache_total_ranks, get_user_rank_from_cache

from pymongo import ReturnDocument

testRouter = APIRouter()

@testRouter.get("/{test_id}", response_model=Test)
async def get_question(test_id: str):
    test = await testCollection.find_one({
        "_id": ObjectId(test_id)
    })

    return test

@testRouter.post("/", status_code=status.HTTP_201_CREATED)
async def create_question(payload: Test):
    test = payload.model_dump(by_alias=True, exclude=["id"])
    res = await testCollection.insert_one(test)

    return {
        "status": "ok",
        "test_id": str(res.inserted_id)
    }

@testRouter.post("/{test_id}/questions", response_model=Test)
async def add_questions_to_test(test_id: str, payload: dict):
    question_ids = payload['questionIds']

    test = await testCollection.find_one_and_update(
        {"_id": ObjectId(test_id)},
        {"$push": {"questions": {"$each": question_ids}}},
        return_document=ReturnDocument.AFTER
    )

    return test


@testRouter.post("/{test_id}/complete")
async def endTest(test_id: str):
    await testCollection.find_one_and_update(
        { "_id": ObjectId(test_id)}, 
        {"$set": { "ongoing": False } }, 
        return_document=ReturnDocument.AFTER
    )

    scores = await calculate_total_scores(test_id)
    await cache_total_ranks(test_id, scores)
    await calculate_subject_percentiles(test_id, scores)

@testRouter.get("/{test_id}/{user_id}/result")
async def getTestResults(test_id: str, user_id: str):
    res = await get_user_rank_from_cache(test_id, user_id)

    return res

@testRouter.post("/{test_id}/predict-mock")
async def predictWithMockScore(test_id: str, payload: dict):
    mock_total = payload['total']
    mock_subject_scores = payload['subject_scores'] 
    predictions = await predict_ranks_percentiles(test_id, mock_total, mock_subject_scores)

    return predictions