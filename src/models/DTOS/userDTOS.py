from datetime import datetime

from pydantic import BaseModel

class RoleMin(BaseModel):
    id: int
    name: str

class getUserResponse(BaseModel):
    id: int
    username: str
    role: RoleMin
    time_updated: datetime

class getUserDetailsResponse(BaseModel):
    id: int
    username: str
    role_id: int
    llm_prefix: str | None = None
    access_token_duration_minutes: int
    time_updated: datetime
    time_created: datetime

class createUserRequest(BaseModel):
    username: str
    password: str
    role_id: int
    access_token_duration_minutes: int
    llm_prefix: str | None = None
class createUserResponse(BaseModel):
    id: int
    username: str
    role: RoleMin
    time_updated: datetime
    
class updateUserRequest(BaseModel):
    username: str
    password: str | None = None
    role_id: int
    llm_prefix: str | None = None
    access_token_duration_minutes: int
    
class updateUserResponse(BaseModel):
    id: int
    username: str
    role: RoleMin
    time_updated: datetime
