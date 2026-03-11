from pydantic import BaseModel
from datetime import datetime

class CommandMin(BaseModel):
    id: int
    name: str

class getMessageResponse(BaseModel):
    id: int
    user_id: int 
    content: str
    is_users: bool
    executed_command: CommandMin | None = None
    time_sent: datetime
    type: str

class createMessageRequest(BaseModel):
    content: str
    send_to_displays: bool | None = False
    type: str

class createMessageResponse(BaseModel):
    user: getMessageResponse
    response: getMessageResponse