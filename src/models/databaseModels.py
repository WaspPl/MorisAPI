from sqlmodel import SQLModel, Field, Relationship, func
from datetime import datetime


class TimestampMixIn(SQLModel):
    time_created: datetime | None = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()}
    )
    time_updated : datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
        }
    )

class RefreshTokens(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(index=True)
    refresh_token: str = Field(index=True, unique=True)

class Role(TimestampMixIn, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, unique=True, nullable=False, min_length=1)

    users: list["User"] = Relationship(back_populates="role")
    command_assignments: list["Command_Role_Assignment"] = Relationship(
        back_populates="role", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"} 
    )



class User(TimestampMixIn, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(index=True, unique=True, nullable=False, min_length=1)
    password: str = Field(nullable=False, min_length=1)
    llm_prefix: str | None = Field(default=None)

    access_token_duration_minutes: int | None = Field(default=30, gt=1)

    role_id: int | None = Field(default=2, foreign_key="role.id")
    role: Role | None = Relationship(back_populates="users")

    messages: list["Message"] = Relationship(back_populates="user")


class Sprite(TimestampMixIn, SQLModel, table=True):
    id: int | None = Field(index=True, default=None, primary_key=True)
    name: str = Field(default= None, unique=True, nullable=False, min_length=1)
    content: str = Field(nullable=False, min_length=1)
    commands: list["Command"] = Relationship(back_populates="sprite")

class Command(TimestampMixIn, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    name: str = Field(nullable=False, min_length=1)
    description: str = Field(nullable=False, min_length=1)
    sprite_repeat_times: int | None = Field(default=1,)
    is_output_llm: bool | None = Field(default=False, nullable=False)
    llm_prefix: str | None = Field(default="")

    script_path: str| None = Field(default=None)
    sprite_id: int | None = Field(default=None, foreign_key="sprite.id", ondelete="RESTRICT")
    sprite: Sprite | None = Relationship(back_populates="commands")


    prompts: list["Prompt"] = Relationship(back_populates="command", cascade_delete=True)
    assignments: list["Command_Role_Assignment"] = Relationship(back_populates="command", cascade_delete=True)
    messages: list["Message"] = Relationship(back_populates='executed_command')

class Prompt(TimestampMixIn, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    text: str = Field(default = None, unique=True, index=True, nullable=True, min_length=1)
    
    command_id: int | None = Field(default=None, foreign_key="command.id", ondelete="CASCADE")
    command: Command | None = Relationship(back_populates="prompts")
    
class Command_Role_Assignment(TimestampMixIn, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    
    command_id: int | None = Field(index=True, default=None, foreign_key="command.id", ondelete="CASCADE") 
    command: Command | None = Relationship(back_populates="assignments")
    
    role_id: int | None = Field(default=None, foreign_key="role.id", ondelete="CASCADE")  
    role: Role | None = Relationship(back_populates="command_assignments")


class Message(TimestampMixIn, SQLModel, table= True):
    id: int | None = Field(index=True, default=None, primary_key= True)

    user_id: int | None = Field(index= True, foreign_key='user.id', ondelete='CASCADE', gt=1)
    user: User | None = Relationship(back_populates="messages")

    is_users: bool = Field(default=True, nullable=False)
    content: str = Field(nullable=False, min_length=1)
    type: str = Field(nullable=False, min_length=1)

    executed_command_id: int | None = Field(default=None, foreign_key='command.id')
    executed_command: Command | None = Relationship(back_populates='messages')
