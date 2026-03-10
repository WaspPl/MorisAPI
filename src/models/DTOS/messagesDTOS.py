from pydantic import BaseModel
from datetime import datetime

class getMessageResponse(BaseModel):
    id: int
    user_id: int 
    content: str
    is_users: bool
    was_command_executed: bool
    time_sent: datetime

class createMessageRequest(BaseModel):
    content: str

class createMessageResponse(BaseModel):
    id: int
    user_id: int 
    
    content: str
    response: str

    was_command_executed: bool

    time_sent: datetime