from pydantic import BaseModel

class RoleMin(BaseModel):
    id: int
    name: str


class getMeResponse(BaseModel):
    id: int
    username: str
    role: RoleMin
    llm_prefix: str

class updateMeRequest(BaseModel):
    username: str
    password: str | None = None
    role_id: int
    llm_prefix: str

class updateMeResponse(BaseModel):
    id: int
    username: str
    role: RoleMin
    llm_prefix: str
    access_token: str
    token_type: str


