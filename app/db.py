import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

load_dotenv()

client = AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.get_database("exams")

userCollection = db.get_collection("users")
testCollection = db.get_collection("tests")
questionCollection = db.get_collection("questions")
submissionCollection = db.get_collection("submissions")

submissionCollection.create_index([
    ("user_id", ASCENDING),
    ("test_id", ASCENDING),
    ("question_id", ASCENDING)
], unique = True)

submissionCollection.create_index([
    ("test_id", ASCENDING),
    ("user_id", ASCENDING)
])

submissionCollection.create_index([
    ("test_id", ASCENDING),
    ("subject", ASCENDING)
])

submissionCollection.create_index([
    ("test_id", ASCENDING),
    ("marks", DESCENDING)
])

