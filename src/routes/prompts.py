from fastapi import APIRouter

router = APIRouter(prefix="/prompts", tags=["prompts"])

@router.get("")
async def get_prompts():
    return {"message": "List of prompts"}

@router.get("/{prompt_id}")
async def get_prompt(prompt_id: str):
    return {"message": f"Prompt with ID {prompt_id}"}

@router.post("")
async def create_prompt():
    return {"message": "Prompt created"}

@router.put("/{prompt_id}")
async def update_prompt(prompt_id: str):
    return {"message": f"Prompt with ID {prompt_id} updated"}

@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str):
    return {"message": f"Prompt with ID {prompt_id} deleted"}
