from fastapi import APIRouter, Depends
from models.databaseModels import User, Role
import models.DTOS.userDTOS as DTO
from typing import Annotated
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from scripts.database import SessionDep
from scripts.dataValidations import enforce_existing, enforce_unique, protect_admin_count
from scripts.auth import get_current_user, get_password_hash, get_admin
from sqlmodel import select, func



router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[DTO.getUserResponse])
async def get_users(session: SessionDep,current_user: Annotated[User,Depends(get_current_user)], offset: int = 0, limit: int = 10):
    result = session.exec(select(User).offset(offset).limit(limit)).all()
    return result

@router.get("/{user_id}", response_model=DTO.getUserDetailsResponse)
async def get_user(user_id: str,session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]):
    userItem = enforce_existing(User, user_id, session)
    return userItem
    
@router.post("", response_model=DTO.createUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(form_data: DTO.createUserRequest, session: SessionDep, current_user: Annotated[User,Depends(get_admin)]):
    enforce_unique(User, User.username, form_data.username, session)

    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")
    
    userModel = User(username=form_data.username, 
                     password=get_password_hash(form_data.password), 
                     role_id = 2,
                     llm_prefix="")

    session.add(userModel)
    session.commit()
    session.refresh(userModel,attribute_names=["role"])

    return userModel

@router.put("/{user_id}", response_model=DTO.updateUserResponse)
async def update_user(user_id: int, user: DTO.updateUserRequest, session: SessionDep , current_user: Annotated[User,Depends(get_admin)]):
    print(user_id)
    print(current_user.id)
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="To edit your own user use the /me endpoint")
    foundUser = enforce_existing(User, user_id, session)
    
    if user.role_id != 1 and foundUser.role_id == 1:
        protect_admin_count(session)
    
    enforce_unique(User,User.username,user.username,session, user_id)
    
    role = enforce_existing(Role, user.role_id, session)
    userData = user.model_dump(exclude_unset=True)
    if user.password:
        userData["password"] = get_password_hash(user.password)
    foundUser.sqlmodel_update(userData)

    session.add(foundUser)
    session.commit()
    session.refresh(foundUser,attribute_names=["role"])

    return foundUser
    
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, session: SessionDep, current_user: Annotated[User,Depends(get_admin)]):
    
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="To delete your own user use the /me endpoint.")
    
    user = enforce_existing(User, user_id, session)
    if user.role_id == 1:
        protect_admin_count(session)

    session.delete(user)
    session.commit()

    return
