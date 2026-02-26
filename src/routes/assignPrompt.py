from fastapi import APIRouter

router = APIRouter(prefix="/assignPrompt", tags=["assignPrompt"])

@router.get("")
async def get_assignPrompt():
    return {"message": "List of assignPrompt"}

@router.get("/{assignPrompt_id}")
async def get_assignPrompt_by_id(assignPrompt_id: str):
    return {"message": f"assignPrompt with ID {assignPrompt_id}"}

@router.post("")
async def create_assignPrompt():
    return {"message": "assignPrompt created"}

@router.put("/{assignPrompt_id}")
async def update_assignPrompt(assignPrompt_id: str):
    return {"message": f"assignPrompt with ID {assignPrompt_id} updated"}

@router.delete("/{assignPrompt_id}")
async def delete_assignPrompt(assignPrompt_id: str):
    return {"message": f"assignPrompt with ID {assignPrompt_id} deleted"}
