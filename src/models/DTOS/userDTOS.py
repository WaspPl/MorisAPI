from pydantic import BaseModel

class getUserResponse(BaseModel):
    id: int
    username: str
    role_name: str

class getUserDetailsResponse(BaseModel):
    id: int
    username: str
    role_id: int

class createUserResponse(BaseModel):
    id: int
    username: str
    role_name: str

class updateUserRequest(BaseModel):
    username: str
    password: str | None = None
    role_id: int


class updateUserResponse(BaseModel):
    id: int
    username: str
    role_name: str
