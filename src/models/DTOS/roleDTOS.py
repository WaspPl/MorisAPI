from pydantic import BaseModel

class GetRoleResponse(BaseModel):
    id: int
    name: str

class CreateRoleRequest(BaseModel):
    name: str

class CreateRoleResponse(BaseModel):
    id: int
    name: str

class UpdateRoleRequest(BaseModel):
    name: str

class UpdateRoleResponse(BaseModel):
    id: int
    name: str