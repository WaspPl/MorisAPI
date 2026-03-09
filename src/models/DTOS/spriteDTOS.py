from pydantic import BaseModel

class getSpriteResponse(BaseModel):
    id: int
    name: str

class getSpriteDetailsResponse(BaseModel):
    id: int
    name: str
    content: str

class createSpriteRequest(BaseModel):
    name: str
    content: str

class createSpriteResponse(BaseModel):
    id: int
    name: str

class updateSpriteRequest(BaseModel):
    name: str
    content: str

class updateSpriteResponse(BaseModel):
    id: int
    name: str