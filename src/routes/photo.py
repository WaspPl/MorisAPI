from fastapi import APIRouter, Depends
from scripts.auth import getCurrentUser

router = APIRouter(prefix="/photo", tags=["photo"])

@router.get("")
async def get_photo(user = Depends(getCurrentUser)):
    # Note to self
    # when adding this remember to make it so that only selected roles can access it 
    return {"message": "Photo Base64 string"}