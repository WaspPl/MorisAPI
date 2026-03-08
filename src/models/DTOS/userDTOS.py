from pydantic import BaseModel

class RoleMin(BaseModel):
    id: int
    name: str

class getUserResponse(BaseModel):
    id: int
    username: str
    role: RoleMin

class getUserDetailsResponse(BaseModel):
    id: int
    username: str
    role_id: int

class createUserResponse(BaseModel):
    id: int
    username: str
    role: RoleMin

class updateUserRequest(BaseModel):
    username: str
    password: str | None = None
    role_id: int


class updateUserResponse(BaseModel):
    id: int
    username: str
    role: RoleMin
