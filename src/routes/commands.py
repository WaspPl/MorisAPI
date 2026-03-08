from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser, getAdmin
from scripts.database import SessionDep, enforceExisting, enforceUnique
from sqlmodel import select
from models.databaseModels import Command, Command_Role_Assignment
import models.DTOS.commandDTOS as DTO
from fastapi import HTTPException, status

router = APIRouter(prefix="/commands", tags=["commands"])

@router.get("", response_model=list[DTO.getCommandResponse])
async def get_commands(session: SessionDep, currentUser = Depends(getCurrentUser), limit: int = 100, offset: int = 0 ):
    commands = session.exec(select(Command).join(Command_Role_Assignment).where(Command_Role_Assignment.role_id == currentUser.role_id).limit(limit).offset(offset)).all()
    return commands

@router.get("/{command_id}", response_model=DTO.getCommandDetailsResponse)
async def get_command(command_id: int, session: SessionDep, currentUser = Depends(getCurrentUser)):
    command = session.exec(select(Command).join(Command_Role_Assignment).where(Command_Role_Assignment.role_id == currentUser.role_id).where(Command.id == command_id)).first()
    if not command:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail="Command not found")
    return command

@router.post("")
async def create_command(user = Depends(getAdmin)):
    return {"message": "Command created"}

@router.put("/{command_id}")
async def update_command(command_id: str, user = Depends(getAdmin)):
    return {"message": f"Command with ID {command_id} updated"}

@router.delete("/{command_id}")
async def delete_command(command_id: str, user = Depends(getAdmin)):
    return {"message": f"Command with ID {command_id} deleted"}
