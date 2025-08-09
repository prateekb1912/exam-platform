from fastapi import FastAPI
from app.routes.user import userRouter
from app.routes.question import questionRouter
from app.routes.test import testRouter
app = FastAPI()

app.include_router(userRouter, prefix='/users', tags=["users"])
app.include_router(questionRouter, prefix='/questions', tags=["questions"])
app.include_router(testRouter, prefix='/tests', tags=["tests"])

@app.get('/')
def hello():
    return {"status": "200 OK"}

