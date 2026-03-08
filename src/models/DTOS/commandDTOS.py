from pydantic import BaseModel

class getCommandResponse(BaseModel):
    id: int
    name: str
    description: str
    script_name: str 
    sprite_name: str
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 
    
class PromptMin(BaseModel):
    id: int
    text: str

class RoleMin(BaseModel):
    id: int
    name: str

class AssignedRoleMin(BaseModel):
    id: int
    role: RoleMin

class getCommandDetailsResponse(BaseModel):
    id: int
    name: str
    description: str
    script_name: str 
    sprite_name: str
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
    scirpt_name: str
    sprite_name: str
    sprite_repeat_times: int
    is_output_llm: bool 
    llm_prefix: str 

class updateCommandRequest(BaseModel):
    name: str
    description: str
    scirpt_name: str
    sprite_name: str
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
 