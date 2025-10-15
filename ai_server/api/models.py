from pydantic import BaseModel, field_validator
import datetime

class PlanRequest(BaseModel):

    starting_point: str
    ending_point: str
    date: datetime.date
    tons: int

    @field_validator('tons')
    @classmethod
    def tons_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Tons must be a positive integer.')
        return v
