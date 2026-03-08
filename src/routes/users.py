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
async def get_users(session: SessionDep, offset: int = 0, limit: int = 100, currentUser = Depends(getCurrentUser)):
    result = session.exec(select(User,Role).where(User.role_id==Role.id).offset(offset).limit(limit))
    response = []
    for user, role in result:
        response.append(DTO.getUserResponse(id=user.id,
                                            username=user.username, 
                                            role_name= role.name))
    return response

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
                     role_id = 2)

    session.add(userModel)
    session.commit()
    session.refresh(userModel,attribute_names=["role"])

    return DTO.createUserResponse(id= userModel.id,
                                  username= userModel.username,
                                  role_name= userModel.role.name)

@router.put("/{user_id}", response_model=DTO.updateUserResponse)
async def update_user(user_id: str, user: DTO.updateUserRequest, session: SessionDep , currentUser = Depends(getAdmin)):
    foundUser = enforceExisting(User, user_id, session)
    if user.role_id != 1 and foundUser.role_id == 1:
        protectAdminCount(session)
    
    role = enforceExisting(Role, user.role_id, session)
    userData = user.model_dump(exclude_unset=True)

    foundUser.sqlmodel_update(userData)

    session.add(foundUser)
    session.commit()
    session.refresh(foundUser,attribute_names=["role"])

    return DTO.updateUserResponse(id= foundUser.id,
                                  username= foundUser.username,
                                  role_name= foundUser.role.name)
    
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
