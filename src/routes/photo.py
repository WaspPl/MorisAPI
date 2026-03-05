from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser

router = APIRouter(prefix="/photo", tags=["photo"])

@router.get("")
async def get_photo(user = Depends(getCurrentUser)):
    return {"message": "Photo Base64 string"}