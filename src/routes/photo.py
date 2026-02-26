from fastapi import APIRouter

router = APIRouter(prefix="/photo", tags=["photo"])

@router.get("")
async def get_photo():
    return {"message": "Photo Base64 string"}