from pydantic import BaseModel

class CommandMin(BaseModel):
    id: int
    name: str

class getPromptResponse(BaseModel):
    id: int
    text: str
    command: CommandMin

class getPromptDetailsResponse(BaseModel):
    id: int
    text: str
    commandId: int

class createPromptRequest(BaseModel):
    text: str
    command_id: int

class createPromptResponse(BaseModel):
    id: int
    text: str
    command: CommandMin

class updatePromptRequest(BaseModel):
    text: str
    command_id: int

class updatePromptResponse(BaseModel):
    text: str
    command: CommandMin