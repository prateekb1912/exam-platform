from fastapi import APIRouter

testRouter = APIRouter()

@testRouter.get("/")
def get_tests():
    return {"tests": []}