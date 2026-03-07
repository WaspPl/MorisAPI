from pydantic import BaseModel

class getUserResponse(BaseModel):
    id: int
    username: str
    roleName: str

class getUserDetailsResponse(BaseModel):
    id: int
    username: str
    roleId: int

class createUserResponse(BaseModel):
    id: int
    username: str
    roleId: int

class updateUserRequest(BaseModel):
    username: str
    password: str | None = None
    roleId: int


class updateUserResponse(BaseModel):
    id: int
    username: str
    roleId: int
