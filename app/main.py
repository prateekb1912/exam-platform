from bson import ObjectId
from datetime import datetime
from fastapi import FastAPI

from app.routes.user import userRouter
from app.routes.question import questionRouter
from app.routes.test import testRouter

from app.schemas import SubmissionPayload, Question
from app.db import userCollection, questionCollection, submissionCollection

app = FastAPI()

app.include_router(userRouter, prefix='/users', tags=["users"])
app.include_router(questionRouter, prefix='/questions', tags=["questions"])
app.include_router(testRouter, prefix='/tests', tags=["tests"])

@app.get('/')
def hello():
    return {"status": "200 OK"}


@app.post('/submit-answer', response_model=SubmissionPayload)
async def submit_answer(payload: SubmissionPayload):
    try:
        submission = payload.model_dump(by_alias=True, exclude=['id'])
        user = await userCollection.find_one({
            "_id": ObjectId(payload.user_id)
        })

        question: Question = await questionCollection.find_one({
            "_id": ObjectId(payload.question_id)
        })
    
    except:
        return {
            "status": "404 NOT FOUND",
            "user_id": payload.user_id,
            "question_id": payload.question_id
        }
    
    submission['is_correct'] = (question['answer_index'] == payload.selected_option)
    submission['marks']= question['marks_correct'] if payload.is_correct else question['marks_incorrect']

    res = await submissionCollection.insert_one(submission)

    return {
        "submission_id": str(res.inserted_id)
    }
