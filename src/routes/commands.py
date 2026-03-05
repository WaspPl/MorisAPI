from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser, getAdmin

router = APIRouter(prefix="/commands", tags=["commands"])

@router.get("")
async def get_commands(user = Depends(getCurrentUser)):
    return {"message": f"List of commands available to the user {user.username}"}

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
