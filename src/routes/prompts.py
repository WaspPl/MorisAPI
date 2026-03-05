from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser, getAdmin

router = APIRouter(prefix="/prompts", tags=["prompts"], dependencies= [Depends(getCurrentUser)],)

@router.get("")
async def get_prompts(user = Depends(getCurrentUser)):
    return {"message": "List of prompts"}

@router.get("/{prompt_id}")
async def get_prompt(prompt_id: str, user = Depends(getCurrentUser)):
    return {"message": f"Prompt with ID {prompt_id}"}

@router.post("")
async def create_prompt(user = Depends(getAdmin)):
    return {"message": "Prompt created"}

@router.put("/{prompt_id}")
async def update_prompt(prompt_id: str, user = Depends(getAdmin)):
    return {"message": f"Prompt with ID {prompt_id} updated"}

@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str, user = Depends(getAdmin)):
    return {"message": f"Prompt with ID {prompt_id} deleted"}
