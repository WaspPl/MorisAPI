from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser, getAdmin
from scripts.database import SessionDep, enforceExisting, enforceUnique
from sqlmodel import select
from models.databaseModels import Command, Command_Role_Assignment, Sprite
import models.DTOS.commandDTOS as DTO
from fastapi import HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from scripts.configToObject import SettingsDep
from pathlib import Path
import shutil

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

@router.post("", status_code=status.HTTP_201_CREATED, response_model=DTO.createCommandResponse)
async def create_command(newCommand: DTO.createCommandRequest, session: SessionDep, currentUser = Depends(getAdmin)):
    
    if newCommand.sprite_id:
        enforceExisting(Sprite, newCommand.sprite_id, session)

    enforceUnique(Command, Command.name, newCommand.name, session)

    command = Command.model_validate(newCommand)
    session.add(command)
    session.commit()
    session.refresh(command)
    defaultAssignment = Command_Role_Assignment(command_id=command.id, role_id=1)
    session.add(defaultAssignment)
    session.commit()

    return command

@router.put("/{command_id}", response_model=DTO.updateCommandResponse)
async def update_command(command_id: str, newCommand: DTO.updateCommandRequest, session: SessionDep, user = Depends(getAdmin)):
    commandItem = enforceExisting(Command, command_id, session)
    enforceExisting(Sprite, newCommand.sprite_id, session)
    enforceUnique(Command, Command.name, newCommand.name, session, command_id)

    commandData = newCommand.model_dump()
    command = commandItem.sqlmodel_update(commandData)

    session.add(command)
    session.commit()
    session.refresh(command)

    return command

@router.delete("/{command_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_command(command_id: str, session: SessionDep, user = Depends(getAdmin)):
    command = enforceExisting(Command, command_id, session)
    if command.script_path and Path(command.script_path).exists():
        Path(command.script_path).unlink()
    session.delete(command)
    session.commit()
    return 

@router.get('/{command_id}/script')
async def download_script(command_id: int, session: SessionDep, settings: SettingsDep, currentUser = Depends(getAdmin)):
    scritps_path = Path(settings.storage.scripts_dir)
    command = enforceExisting(Command, command_id, session)
    if not command.script_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="This command has no script yet.")
    return FileResponse(path=command.script_path, filename=f"script_{command_id}.py")
@router.put('/{command_id}/script')
async def upload_script(command_id: int, session: SessionDep,settings: SettingsDep , file: UploadFile = File(...), currentUser = Depends(getAdmin)):
    scritps_path = Path(settings.storage.scripts_dir)    
    scritps_path.mkdir(parents=True, exist_ok=True)

    command = enforceExisting(Command, command_id, session)

    file_extension = Path(file.filename).suffix
    if file_extension != ".py":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Script has to be in a .py format")


    file_path = scritps_path / f"command_{command_id}.py"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    command.script_path = str(file_path)
    session.add(command)
    session.commit()
    return
