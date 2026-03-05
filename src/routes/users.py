from fastapi import APIRouter, Depends
from models.databaseModels import Users
import models.DTOS.usersDTOS as DTO
from typing import Annotated
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from scripts.database import SessionDep
from scripts.auth import getUser, getCurrentUser, getPasswordHash


router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(getCurrentUser)])

@router.get("")
async def get_users():
    return {"message": "List of users"}

@router.get("/{user_id}")
async def get_user(user_id: str):
    return {"message": f"User with ID {user_id}"}

# Note: The create_user enpoint does not exist, because of the authentication system. Users are created through the /auth/register endpoint.
@router.post("", response_model=DTO.createUserResponse)
async def register(formData: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    existingUser = getUser(formData.username, session)
    if existingUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with that username already exists")
    
    if not formData.username or not formData.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

    passwordHash = getPasswordHash(formData.password)
    
    userModel = Users(username=formData.username, hashed_password=passwordHash, roleId=1)

    userItem = Users.model_validate(userModel)
    session.add(userItem)
    session.commit()
    session.refresh(userItem)

    return userItem

@router.put("/{user_id}")
async def update_user(user_id: str):
    return {"message": f"User with ID {user_id} updated"}

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    return {"message": f"User with ID {user_id} deleted"}
