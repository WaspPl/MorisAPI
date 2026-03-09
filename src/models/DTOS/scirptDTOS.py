from pydantic import BaseModel

class getScriptResponse(BaseModel):
    id: int
    name: str

class getScriptDetailsResponse(BaseModel):
    id: int
    name: str
    content: str

class createScriptRequest(BaseModel):
    name: str
    content: str

class createScriptResponse(BaseModel):
    id: int
    name: str

class updateScriptRequest(BaseModel):
    name: str
    content: str

class updateScriptResponse(BaseModel):
    id: int
    name: str