from pydantic import BaseModel

class getPromptResponse(BaseModel):
    id: int
    text: str
    commandName: str

class getPromptDetailsResponse(BaseModel):
    id: int
    text: str
    commandId: int

class createPromptRequest(BaseModel):
    text: str
    commandId: int

class createPromptResponse(BaseModel):
    id: int
    text: str
    commandName: str