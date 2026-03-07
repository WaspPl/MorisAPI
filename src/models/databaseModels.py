from sqlmodel import SQLModel, Field


    
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    username: str = Field(index = True, unique= True)
    hashed_password: str
    roleId: int | None = Field(default = None, foreign_key="role.id",)

class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    name: str = Field(index=True, unique=True)

class Command_Role_Assignment(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    commandId: int | None = Field(index = True, default=None, foreign_key="command.id", ondelete="CASCADE") 
    roleId: int | None = Field(default=None, foreign_key="role.id", ondelete="CASCADE")  

class Command(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    description: str
    script_name: str = Field(unique=True)
    spriteName: str
    sprite_repeat_times: int
    is_output_llm: bool | None = False
    llm_prefix: str = Field(default="")
    
class Prompt(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True, index = True)
    content: str = Field(unique=True, index = True)
    commandId: int | None = Field(default = None, foreign_key="command.id", ondelete="CASCADE")