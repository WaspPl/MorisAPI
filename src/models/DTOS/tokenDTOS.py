from pydantic import BaseModel

class loginResponse(BaseModel):
    access_token: str
    token_type: str
