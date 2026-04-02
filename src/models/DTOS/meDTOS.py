from datetime import datetime

from pydantic import BaseModel


class getMeResponse(BaseModel):
    id: int
    username: str
    role_id: int
    llm_prefix: str
    token_duration_minutes: int
    time_updated: datetime
    time_created: datetime

class updateMeRequest(BaseModel):
    username: str
    password: str | None = None
    role_id: int
    llm_prefix: str
    token_duration_minutes: int

class updateMeResponse(BaseModel):
    id: int
    username: str
    role_id: int
    llm_prefix: str
    token_duration_minutes: int
    time_updated: datetime
    time_created: datetime
    access_token: str
    token_type: str


