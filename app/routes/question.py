from bson import ObjectId
from fastapi import APIRouter, status

from app.db import questionCollection
from app.schemas import Question

questionRouter = APIRouter()

@questionRouter.get("/{question_id}", response_model=Question)
async def get_question(question_id: str):
    question = await questionCollection.find_one({
        "_id": ObjectId(question_id)
    })

    return question

@questionRouter.post("/", status_code=status.HTTP_201_CREATED)
async def create_question(payload: Question):
    question = payload.model_dump(by_alias=True, exclude=["id"])
    res = await questionCollection.insert_one(question)

    return {
        "status": "ok",
        "question_id": str(res.inserted_id)
    }
