from pydantic import BaseModel

class createAssignmentRequest(BaseModel):
    command_id: int
    role_id: int

class createAssignmentResponse(BaseModel):
    id: int
    command_id: int
    role_name: str

