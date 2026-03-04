from sqlmodel import SQLModel, Field


    
class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    username: str = Field(index = True, unique= True)
    hashed_password: str
    roleId: int | None = Field(default = None, foreign_key="roles.id", ondelete="SET NULL")

class Roles(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    name: str = Field(index=True, unique=True)

class Command_Role_Assignments(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    commandId: int | None = Field(index = True, default=None, foreign_key="commands.id", ondelete="CASCADE") 
    roleId: int | None = Field(default=None, foreign_key="roles.id", ondelete="CASCADE")  

class Commands(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    description: str
    script_name: str = Field(unique=True)
    spriteName: str
    sprite_repeat_times: int
    is_output_llm: bool | None = False
    llm_prefix: str = Field(default="")
    
class Prompts(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    content: str = Field(unique=True, index = True)
    commandId: int | None = Field(default = None, foreign_key="commands.id", ondelete="CASCADE")