import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

client = AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.get_database("exams")

userCollection = db.get_collection("users")
testCollection = db.get_collection("tests")
questionCollection = db.get_collection("questions")
submissionCollection = db.get_collection("submissions")