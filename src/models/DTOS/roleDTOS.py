from datetime import datetime

from pydantic import BaseModel

class GetRoleResponse(BaseModel):
    id: int
    name: str
    time_updated: datetime

class GetRoleDetailsResponse(BaseModel):
    id: int
    name: str
    time_updated: datetime
    time_created: datetime


class CreateRoleRequest(BaseModel):
    name: str

class CreateRoleResponse(BaseModel):
    id: int
    name: str
    time_updated: datetime

class UpdateRoleRequest(BaseModel):
    name: str

class UpdateRoleResponse(BaseModel):
    id: int
    name: str
    time_updated: datetime