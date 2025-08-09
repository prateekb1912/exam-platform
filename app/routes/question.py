from fastapi import APIRouter

questionRouter = APIRouter()

@questionRouter.get("/")
def get_questions():
    return {"questions": []}