from pydantic import BaseModel

class getPromptResponse(BaseModel):
    id: int
    text: str
    command_name: str

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
    command_name: str

class updatePromptRequest(BaseModel):
    text: str
    command_id: int

class updatePromptResponse(BaseModel):
    text: str
    command_name: str