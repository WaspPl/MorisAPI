from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser, getAdmin

router = APIRouter(prefix="/assignRole", tags=["assignRole"])

@router.post("")
async def create_assignPrompt(user = Depends(getAdmin)):
    return {"message": "assignPrompt created"}


@router.delete("/{assignPrompt_id}")
async def delete_assignPrompt(assignPrompt_id: str, user = Depends(getAdmin)):
    return {"message": f"assignPrompt with ID {assignPrompt_id} deleted"}
