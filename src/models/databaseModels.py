from scripts.database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean

class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    RoleId = Column(Integer, ForeignKey("roles.id", ondelete="SET DEFAULT"),default=0)
    
class Roles(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Command_Role_Assignments(Base):
    __tablename__ = "command_role_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    CommandId = Column(Integer, ForeignKey("commands.id", ondelete="CASCADE"))
    RoleId = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))
    
class Commands(Base):
    __tablename__ = "commands"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    script_name = Column(String, unique=True, index=True)
    spriteName = Column(String)
    sprite_repeat_times = Column(Integer)
    is_output_llm = Column(Boolean, default=False)
    llm_prefix = Column(Text, default="")
    
class Prompts(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    commandId = Column(Integer, ForeignKey("commands.id", ondelete="CASCADE"))