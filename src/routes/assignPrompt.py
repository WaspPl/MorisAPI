from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser, getAdmin

router = APIRouter(prefix="/assignPrompt", tags=["assignPrompt"])

@router.get("")
async def get_assignPrompt(user = Depends(getCurrentUser)):
    return {"message": "List of assignPrompt"}

@router.get("/{assignPrompt_id}")
async def get_assignPrompt_by_id(assignPrompt_id: str, user = Depends(getCurrentUser)):
    return {"message": f"assignPrompt with ID {assignPrompt_id}"}

@router.post("")
async def create_assignPrompt(user = Depends(getAdmin)):
    return {"message": "assignPrompt created"}

@router.put("/{assignPrompt_id}")
async def update_assignPrompt(assignPrompt_id: str, user = Depends(getAdmin)):
    return {"message": f"assignPrompt with ID {assignPrompt_id} updated"}

@router.delete("/{assignPrompt_id}")
async def delete_assignPrompt(assignPrompt_id: str, user = Depends(getAdmin)):
    return {"message": f"assignPrompt with ID {assignPrompt_id} deleted"}
