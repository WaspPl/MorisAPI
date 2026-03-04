from pydantic import BaseModel

class loginResponse(BaseModel):
    token: str

class registerResponse(BaseModel):
    id: int
    username: str
    roleId: int