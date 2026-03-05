from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser

router = APIRouter(prefix="/status", tags=["status"])

@router.get("")
async def get_status(user = Depends(getCurrentUser)):
    return {"message": "System status is healthy"}