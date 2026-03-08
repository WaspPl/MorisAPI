from pydantic import BaseModel

class RoleMin(BaseModel):
    id: int
    name: str

class createAssignmentRequest(BaseModel):
    command_id: int
    role_id: int

class createAssignmentResponse(BaseModel):
    id: int
    command_id: int
    role: RoleMin

