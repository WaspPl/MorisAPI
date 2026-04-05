from pydantic import BaseModel

class loginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    refresh_token_duration_days: int
    access_token_duration_minutes: int
