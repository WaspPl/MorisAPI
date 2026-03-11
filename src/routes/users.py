from fastapi import APIRouter, Depends
from models.databaseModels import User, Role
import models.DTOS.userDTOS as DTO
from typing import Annotated
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from scripts.database import SessionDep, enforceExisting, enforceUnique, protectAdminCount
from scripts.auth import getUser, getCurrentUser, getPasswordHash, getAdmin
from sqlmodel import select, func


router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[DTO.getUserResponse])
async def get_users(session: SessionDep, offset: int = 0, limit: int = 10, currentUser = Depends(getCurrentUser)):
    result = session.exec(select(User).offset(offset).limit(limit)).all()
    return result

@router.get("/{user_id}", response_model=DTO.getUserDetailsResponse)
async def get_user(user_id: str,session: SessionDep, currentUser = Depends(getCurrentUser)):
    userItem = enforceExisting(User, user_id, session)
    return userItem
    
@router.post("", response_model=DTO.createUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(formData: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep, user = Depends(getAdmin)):
    enforceUnique(User, User.username, formData.username, session)

    if not formData.username or not formData.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")
    
    userModel = User(username=formData.username, 
                     password=getPasswordHash(formData.password), 
                     role_id = 2,
                     llm_prefix="")

    session.add(userModel)
    session.commit()
    session.refresh(userModel,attribute_names=["role"])

    return userModel

@router.put("/{user_id}", response_model=DTO.updateUserResponse)
async def update_user(user_id: str, user: DTO.updateUserRequest, session: SessionDep , currentUser = Depends(getAdmin)):
    if currentUser.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="To edit your own user use the /me endpoint")
    foundUser = enforceExisting(User, user_id, session)
    
    if user.role_id != 1 and foundUser.role_id == 1:
        protectAdminCount(session)
    
    enforceUnique(User,User.username,user.username,session, user_id)
    
    role = enforceExisting(Role, user.role_id, session)
    userData = user.model_dump(exclude_unset=True)
    if user.password:
        userData["password"] = getPasswordHash(user.password)
    foundUser.sqlmodel_update(userData)

    session.add(foundUser)
    session.commit()
    session.refresh(foundUser,attribute_names=["role"])

    return foundUser
    
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, session: SessionDep, currentUser = Depends(getAdmin)):
    
    if user_id == currentUser.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="To delete your own user use the /me endpoint.")
    
    user = enforceExisting(User, user_id, session)
    if user.role_id == 1:
        protectAdminCount(session)

    session.delete(user)
    session.commit()

    return
