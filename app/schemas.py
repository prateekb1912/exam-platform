from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, Optional

PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class Test(BaseModel):
    title: str
    duration: int
    questions: list[str] = []

class Question(BaseModel):
    test_id: str
    query: str
    options: list[str]
    answer_index: int
    marks_correct: int = 5
    marks_incorrect: int = -1
    subject: str