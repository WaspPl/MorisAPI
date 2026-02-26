from fastapi import APIRouter

router = APIRouter(prefix="/commands", tags=["commands"])

@router.get("")
async def get_commands():
    return {"message": "List of commands"}

@router.get("/{command_id}")
async def get_command(command_id: str):
    return {"message": f"Command with ID {command_id}"}

@router.post("")
async def create_command():
    return {"message": "Command created"}

@router.put("/{command_id}")
async def update_command(command_id: str):
    return {"message": f"Command with ID {command_id} updated"}

@router.delete("/{command_id}")
async def delete_command(command_id: str):
    return {"message": f"Command with ID {command_id} deleted"}
