from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("")
async def get_messages(user = Depends(getCurrentUser)):
    return {"message": "List of messages"}

@router.post("")
async def create_message(user = Depends(getCurrentUser)):
    return {"message": "Message created"}