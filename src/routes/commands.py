from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser, getAdmin
from scripts.database import SessionDep, enforceExisting, enforceUnique
from sqlmodel import select
from models.databaseModels import Command, Command_Role_Assignment

router = APIRouter(prefix="/commands", tags=["commands"])

@router.get("")
async def get_commands(session: SessionDep, currentUser = Depends(getCurrentUser), limit: int = 100, offset: int = 0 ):
    commands = session.exec(select(Command).join(Command_Role_Assignment).where(Command_Role_Assignment.role_id == currentUser.role_id).limit(limit).offset(offset)).all()
    return commands

@router.get("/{command_id}")
async def get_command(command_id: str, user = Depends(getCurrentUser)):
    return {"message": f"Command with ID {command_id}"}

@router.post("")
async def create_command(user = Depends(getAdmin)):
    return {"message": "Command created"}

@router.put("/{command_id}")
async def update_command(command_id: str, user = Depends(getAdmin)):
    return {"message": f"Command with ID {command_id} updated"}

@router.delete("/{command_id}")
async def delete_command(command_id: str, user = Depends(getAdmin)):
    return {"message": f"Command with ID {command_id} deleted"}
