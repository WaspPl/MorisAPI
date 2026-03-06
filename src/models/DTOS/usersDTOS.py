from pydantic import BaseModel

class getUserResponse(BaseModel):
    id: int
    username: str
    roleName: str

class createUserResponse(BaseModel):
    id: int
    username: str
    roleId: int
