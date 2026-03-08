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

class ScriptMin(BaseModel):
    id: int
    name: str

class SpriteMin(BaseModel):
    id: int
    name: str

class getCommandResponse(BaseModel):
    id: int
    name: str
    description: str
    script: ScriptMin
    sprite: SpriteMin
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 
    
class getCommandDetailsResponse(BaseModel):
    id: int
    name: str
    description: str
    script:  ScriptMin
    sprite: SpriteMin
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 
    prompts: list[PromptMin]
    assignments: list[AssignedRoleMin]

class createCommandRequest(BaseModel):
    name: str
    description: str
    scirpt_name: str
    sprite_name: str
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 

class createCommandResponse(BaseModel):
    id: int
    name: str
    description: str
    scirpt: ScriptMin
    sprite: SpriteMin
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 

class updateCommandRequest(BaseModel):
    name: str
    description: str
    scirpt_id: str
    sprite_id: str
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 

class updateCommandResponse(BaseModel):
    id: int
    name: str
    description: str
    scirpt_name: str
    sprite_name: str
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 
 