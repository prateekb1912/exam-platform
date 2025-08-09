from bson import ObjectId
from fastapi import APIRouter, status

from app.schemas import User
from app.db import userCollection


userRouter = APIRouter()

@userRouter.get("/{user_id}", response_model=User)
async def get_users(user_id: str):
    user = await userCollection.find_one({
        "_id": ObjectId(user_id)
    })
    return user

@userRouter.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(payload: User):
    user = payload.model_dump(by_alias=True, exclude=["id"])
    res = await userCollection.insert_one(user)
    
    return {
        "status": "ok",
        "user_id": str(res.inserted_id)
    }
