from pydantic import BaseModel

class createUserResponse(BaseModel):
    id: int
    username: str
    roleId: int