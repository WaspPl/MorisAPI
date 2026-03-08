from sqlmodel import SQLModel, Field, Relationship

class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)

    users: list["User"] = Relationship(back_populates="role")
    command_assignments: list["Command_Role_Assignment"] = Relationship(back_populates="role")
    
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(index=True, unique=True)
    password: str

    role_id: int | None = Field(default=2, foreign_key="role.id")
    role: Role | None = Relationship(back_populates="users")

class Script(SQLModel, table=True):
    id: int | None = Field(index=True, default=None, primary_key=True)
    name: str | None = Field(unique=True)
    content: str
    commands: list["Command"] = Relationship(back_populates="script")

class Sprite(SQLModel, table=True):
    id: int | None = Field(index=True, default=None, primary_key=True)
    name: str | None = Field(unique=True)
    contentBase64: str
    commands: list["Command"] = Relationship(back_populates="sprite")

class Command(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str
    description: str
    sprite_repeat_times: int
    is_output_llm: bool | None = False
    llm_prefix: str = Field(default="")

    script_id: int | None = Field(default=None, foreign_key="script.id", ondelete="RESTRICT")
    script: Script | None = Relationship(back_populates="commands")

    sprite_id: int | None = Field(default=None, foreign_key="sprite.id", ondelete="RESTRICT")
    sprite: Sprite | None = Relationship(back_populates="commands")


    prompts: list["Prompt"] = Relationship(back_populates="command", cascade_delete=True)
    assignments: list["Command_Role_Assignment"] = Relationship(back_populates="command", cascade_delete=True)
    
class Prompt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    text: str = Field(unique=True, index=True)
    
    command_id: int | None = Field(default=None, foreign_key="command.id", ondelete="CASCADE")
    command: Command | None = Relationship(back_populates="prompts")

class Command_Role_Assignment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    
    command_id: int | None = Field(index=True, default=None, foreign_key="command.id", ondelete="CASCADE") 
    command: Command | None = Relationship(back_populates="assignments")
    
    role_id: int | None = Field(default=None, foreign_key="role.id", ondelete="CASCADE")  
    role: Role | None = Relationship(back_populates="command_assignments")