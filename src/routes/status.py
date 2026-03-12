from fastapi import APIRouter, Depends
from scripts.auth import get_current_user
from typing import Annotated
from models.databaseModels import User


router = APIRouter(prefix="/status", tags=["status"])

@router.get("")
async def get_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"message": "System status is healthy"}