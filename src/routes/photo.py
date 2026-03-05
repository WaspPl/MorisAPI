from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser

router = APIRouter(prefix="/photo", tags=["photo"], dependencies= [Depends(getCurrentUser)],)

@router.get("")
async def get_photo():
    return {"message": "Photo Base64 string"}