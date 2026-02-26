from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("")
async def get_messages():
    return {"message": "List of messages"}

@router.post("")
async def create_message():
    return {"message": "Message created"}