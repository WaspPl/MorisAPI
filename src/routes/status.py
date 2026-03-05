from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser

router = APIRouter(prefix="/status", tags=["status"],dependencies= [Depends(getCurrentUser)],)

@router.get("")
async def get_status():
    return {"message": "System status is healthy"}