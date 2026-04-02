from datetime import datetime

from pydantic import BaseModel

class getSpriteResponse(BaseModel):
    id: int
    name: str
    time_updated: datetime

class getSpriteDetailsResponse(BaseModel):
    id: int
    name: str
    content: str
    time_updated: datetime
    time_created: datetime

class createSpriteRequest(BaseModel):
    name: str
    content: str

class createSpriteResponse(BaseModel):
    id: int
    name: str
    time_updated: datetime

class updateSpriteRequest(BaseModel):
    name: str
    content: str

class updateSpriteResponse(BaseModel):
    id: int
    name: str
    time_updated: datetime