from fastapi import APIRouter

userRouter = APIRouter()

@userRouter.get("/")
def get_users():
    return {"users": []}