from datetime import datetime

from pydantic import BaseModel

class PromptMin(BaseModel):
    id: int
    text: str

class RoleMin(BaseModel):
    id: int
    name: str

class AssignedRoleMin(BaseModel):
    id: int
    role: RoleMin

class SpriteMin(BaseModel):
    id: int
    name: str

class getCommandResponse(BaseModel):
    id: int
    name: str
    description: str
    sprite: SpriteMin | None
    is_output_llm: bool 
    time_updated: datetime
    
class getCommandDetailsResponse(BaseModel):
    id: int
    name: str
    description: str
    sprite_id: int | None
    # sprite: SpriteMin | None
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str | None
    prompts: list[PromptMin]
    assignments: list[AssignedRoleMin]
    time_updated: datetime
    time_created: datetime

class createCommandRequest(BaseModel):
    name: str
    description: str
    sprite_id: int | None = None
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str | None = None

class createCommandResponse(BaseModel):
    id: int
    name: str
    description: str
    sprite: SpriteMin | None = None
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str | None = None
    time_updated: datetime

class updateCommandRequest(BaseModel):
    name: str
    description: str 
    sprite_id: int | None = None
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str | None = None


class updateCommandResponse(BaseModel):
    id: int
    name: str
    description: str
    sprite: SpriteMin | None = None
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str | None = None
    time_updated: datetime
    

 