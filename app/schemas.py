from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, Optional
from datetime import datetime
PyObjectId = Annotated[str, BeforeValidator(str)]

model_config = ConfigDict(
    populate_by_name=True,
    json_encoders={ObjectId: str}
)


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    model_config = model_config

class Test(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)    
    title: str
    duration: Optional[int] = 180
    questions: Optional[list[str]] = []

class Question(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    query: str
    options: list[str]
    answer_index: int
    marks_correct: Optional[int] = 5
    marks_incorrect: Optional[int] = -1
    subject: str

class SubmissionPayload(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    question_id: str
    test_id: str
    selected_option: int

class SubmissionResponse(SubmissionPayload):
    subject: str
    marks: int
    submitted_at: datetime
