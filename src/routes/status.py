from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["status"])

@router.get("")
async def get_status():
    return {"message": "System status is healthy"}