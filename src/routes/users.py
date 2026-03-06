from fastapi import APIRouter, Depends
from models.databaseModels import Users, Roles
import models.DTOS.usersDTOS as DTO
from typing import Annotated
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from scripts.database import SessionDep
from scripts.auth import getUser, getCurrentUser, getPasswordHash, getAdmin
from sqlmodel import select


router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[DTO.getUserResponse])
async def get_users(session: SessionDep, user = Depends(getCurrentUser)):
    statement = select(Users,Roles).where(Users.roleId==Roles.id)
    result = session.exec(statement)
    
    response = []
    for user, role in result:
        response.append(DTO.getUserResponse(id=user.id,username=user.username, roleName= role.name))
    

    return response

@router.get("/{user_id}")
async def get_user(user_id: str, user = Depends(getCurrentUser)):
    return {"message": f"User with ID {user_id}"}

# Note: The create_user enpoint does not exist, because of the authentication system. Users are created through the /auth/register endpoint.
@router.post("", response_model=DTO.createUserResponse)
async def register(formData: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep, user = Depends(getAdmin)):
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
async def update_user(user_id: str, user = Depends(getAdmin)):
    return {"message": f"User with ID {user_id} updated"}

@router.delete("/{user_id}")
async def delete_user(user_id: str, user = Depends(getAdmin)):
    return {"message": f"User with ID {user_id} deleted"}
